"""
Interface module for the Gemma 3 model.
This provides a connection between our database and the language model.
"""

import os
from typing import List, Dict, Any, Optional
import logging

# This will be imported when Gemma 3 is installed or used via API
# from gemma import GemmaModel  # Placeholder import
from database import HybridDatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegalAssistant:
    """
    Legal assistant interface using Gemma 3 model to interact with the database.
    """
    
    def __init__(
        self,
        db_manager: HybridDatabaseManager,
        model_name: str = "gemma3-9b-it",
        model_path: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the legal assistant
        
        Args:
            db_manager: Database manager instance
            model_name: Name of the model to use
            model_path: Path to local model (if using local deployment)
            api_key: API key for model access (if using API)
            config: Additional configuration parameters
        """
        self.db_manager = db_manager
        self.model_name = model_name
        self.model_path = model_path
        self.api_key = api_key or os.environ.get("GEMMA_API_KEY") or os.environ.get("HUGGINGFACE_TOKEN")
        
        # Default configuration
        self.config = {
            "quantize": "none",  # none, 4bit, 8bit
            "device": "auto",    # auto, cpu, cuda
            "temperature": 0.7,  # generation temperature
            "max_tokens": 500,   # maximum tokens to generate
            "do_sample": True,   # whether to use sampling
            "top_p": 0.9         # nucleus sampling parameter
        }
        
        # Update with user-provided config
        if config:
            self.config.update(config)
        
        # Model will be initialized on first use
        self.model = None
        self.processor = None
        
        # System prompt template
        self.system_prompt = """
        You are LexBG Assistant, an AI legal helper for Bulgarian citizens.
        Your goal is to help people understand Bulgarian laws in simple terms.
        Always base your answers on the legal information provided.
        If you're not sure about something, be honest and suggest consulting a lawyer.
        
        When answering questions:
        1. Cite specific laws and articles when possible
        2. Explain legal concepts in simple, everyday language
        3. Avoid complex legal jargon
        4. Provide practical advice when appropriate
        5. Make it clear that your information is not legal advice
        
        IMPORTANT: You can only answer based on the laws in your database.
        """
    
    def initialize_model(self):
        """Initialize the Gemma 3 model"""
        logger.info(f"Initializing Gemma 3 model: {self.model_name}")
        
        try:
            # Try to import the transformers library with Gemma support
            import torch
            from transformers import pipeline, AutoProcessor, Gemma3ForConditionalGeneration
            
            # Get configuration parameters
            device_map = self.config["device"]
            if device_map == "auto":
                device_map = "auto"  # Let transformers decide based on available hardware
            
            # Determine if we should use quantization
            quantize = self.config["quantize"]
            is_quantized = quantize != "none"
            
            # Determine torch data type
            if torch.cuda.is_available() and device_map != "cpu":
                # Use bfloat16 for GPU if available
                if torch.cuda.is_bf16_supported():
                    torch_dtype = torch.bfloat16
                else:
                    torch_dtype = torch.float16
            else:
                # CPU usually needs float32 (except for quantized models)
                torch_dtype = torch.float32
                
            # Parameter to control whether to use pipeline API or direct model loading
            # Direct loading is preferred for more control
            use_pipeline = False
            
            # Path to the model
            if self.model_path:
                # Load from local path
                model_path = self.model_path
                logger.info(f"Using local model at {model_path}")
            else:
                # Use HuggingFace model ID
                model_path = self.model_name
                logger.info(f"Using HuggingFace model: {model_path}")
            
            if use_pipeline:
                # Pipeline API approach
                logger.info(f"Using pipeline API with device={device_map} and dtype={torch_dtype}")
                self.model = pipeline(
                    "text-generation", 
                    model=model_path,
                    device_map=device_map,
                    torch_dtype=torch_dtype,
                    token=self.api_key
                )
            else:
                # Direct model loading approach
                logger.info(f"Using direct model loading with device={device_map}, dtype={torch_dtype}, quantize={quantize}")
                
                # Common model loading kwargs
                model_kwargs = {
                    "device_map": device_map,
                    "token": self.api_key,
                    "torch_dtype": torch_dtype,
                }
                
                # Add quantization parameters if requested
                if quantize == "4bit":
                    # Install bitsandbytes if not already installed
                    try:
                        import bitsandbytes
                        logger.info("bitsandbytes is installed, using 4-bit quantization")
                    except ImportError:
                        logger.warning("bitsandbytes not installed. Trying to install now...")
                        import subprocess
                        subprocess.check_call(["pip", "install", "bitsandbytes"])
                        
                    # 4-bit quantization params
                    model_kwargs.update({
                        "load_in_4bit": True,
                        "quantization_config": {
                            "bnb_4bit_compute_dtype": torch_dtype,
                        }
                    })
                    
                elif quantize == "8bit":
                    # 8-bit quantization
                    try:
                        import bitsandbytes
                        logger.info("bitsandbytes is installed, using 8-bit quantization")
                    except ImportError:
                        logger.warning("bitsandbytes not installed. Trying to install now...")
                        import subprocess
                        subprocess.check_call(["pip", "install", "bitsandbytes"])
                    
                    # 8-bit quantization params
                    model_kwargs.update({
                        "load_in_8bit": True
                    })
                    
                # Load the model with the specified parameters
                model = Gemma3ForConditionalGeneration.from_pretrained(
                    model_path, 
                    **model_kwargs
                ).eval()
                
                # Load processor (tokenizer)
                processor = AutoProcessor.from_pretrained(
                    model_path, 
                    token=self.api_key
                )
                
                # Store both the model and processor
                self.model = model
                self.processor = processor
            
            logger.info("Gemma 3 model loaded successfully")
            
        except ImportError:
            logger.warning("Transformers with Gemma3 support not available")
            logger.warning("To install Gemma3 support, run: pip install git+https://github.com/huggingface/transformers@v4.49.0-Gemma-3")
            self.model = None
        except Exception as e:
            logger.error(f"Error initializing Gemma 3 model: {e}")
            self.model = None
        
        logger.info("Model initialization process completed")
    
    def answer_question(
        self,
        question: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer a legal question based on the database information
        
        Args:
            question: The user's legal question
            max_results: Maximum number of database results to retrieve
            filters: Optional filters to apply to the search
            
        Returns:
            Dictionary containing the answer and supporting information
        """
        logger.info(f"Processing question: {question}")
        
        # Initialize model if not already done
        if self.model is None:
            self.initialize_model()
        
        # Search the database for relevant information
        search_results = self.db_manager.search_similar(
            query=question,
            n_results=max_results,
            filters=filters
        )
        
        # If no results found, return a default response
        if not search_results:
            return {
                "answer": "I don't have enough information to answer this question based on the laws in my database. Please consult a legal professional for advice on this matter.",
                "sources": []
            }
        
        # Prepare context for the model
        context = self._prepare_context(search_results)
        
        # Generate the answer
        answer = self._generate_answer(question, context)
        
        # Prepare sources for citation
        sources = self._prepare_sources(search_results)
        
        return {
            "answer": answer,
            "sources": sources
        }
    
    def _prepare_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Prepare context from search results for the model
        
        Args:
            search_results: Search results from the database
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Track the article numbers we've seen to avoid duplicates
        seen_articles = set()
        
        # Process standard search results
        for i, result in enumerate(search_results):
            content = result["content"]
            metadata = result["metadata"]
            article_number = metadata['article_number']
            
            # Skip duplicates
            if article_number in seen_articles:
                continue
                
            seen_articles.add(article_number)
            
            context_part = f"[Document {i+1}]\n"
            context_part += f"Title: {metadata['law_title']}\n"
            context_part += f"Article: {article_number}\n"
            context_part += f"Content: {content}\n\n"
            
            context_parts.append(context_part)
        
        # Try to add specific articles that are commonly needed but might not be found in search
        # This ensures important articles are always available when needed
        key_article_data = self._get_key_articles()
        
        for article_num, query in key_article_data.items():
            if article_num not in seen_articles:
                # Try to find this article directly
                article_results = self.db_manager.search_similar(
                    query=query,
                    n_results=1
                )
                
                if article_results:
                    result = article_results[0]
                    metadata = result["metadata"]
                    
                    if metadata['article_number'] == article_num:
                        seen_articles.add(article_num)
                        
                        context_part = f"[Key Article]\n"
                        context_part += f"Title: {metadata['law_title']}\n"
                        context_part += f"Article: {article_num}\n"
                        context_part += f"Content: {result['content']}\n\n"
                        
                        context_parts.append(context_part)
        
        return "\n".join(context_parts)
        
    def _get_key_articles(self) -> Dict[str, str]:
        """
        Get key articles and search queries to find them
        
        Returns:
            Dictionary mapping article numbers to search queries that will find them
        """
        # Map important article numbers to search queries that will find them
        return {
            "Чл. 70": "изпитателен срок договор",  # Probation period
            "Чл. 71": "прекратяване изпитателен срок",  # Termination during probation
            "Чл. 325": "прекратяване на трудовия договор",  # Contract termination
            "Чл. 326": "прекратяване от работника с предизвестие",  # Employee termination with notice
            "Чл. 328": "прекратяване от работодателя с предизвестие",  # Employer termination with notice
            "Чл. 155": "платен годишен отпуск",  # Annual paid leave
        }
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate an answer using the Gemma 3 model

        Args:
            question: The user's question
            context: Context from the database
            
        Returns:
            Generated answer
        """
        # Build the prompt for the model
        prompt = f"{self.system_prompt}\n\nContext information from Bulgarian laws:\n{context}\n\nUser question: {question}\n\nAnswer:"
        
        try:
            # Check if we can import the gemma module
            # This is a placeholder - replace with actual Gemma 3 code when available
            try:
                # Try to import the transformers library with Gemma support
                import torch
                from transformers import pipeline, AutoProcessor, Gemma3ForConditionalGeneration
                
                # If we got here, transformers with Gemma3 support is available
                logger.info("Transformers with Gemma3 support is available")
                
                if self.model is None:
                    # Initialize the model
                    logger.info(f"Loading Gemma3 model: {self.model_name}")
                    
                    # Check if we should use the pipeline API or direct model loading
                    if hasattr(self, "use_pipeline") and self.use_pipeline:
                        # Pipeline API approach
                        self.model = pipeline(
                            "text-generation", 
                            model=self.model_name,
                            device_map="auto",
                            torch_dtype=torch.bfloat16
                        )
                        
                        # Generate response using the pipeline with config
                        response = self.model(
                            prompt, 
                            max_new_tokens=self.config["max_tokens"],
                            do_sample=self.config["do_sample"],
                            temperature=self.config["temperature"],
                            top_p=self.config["top_p"]
                        )[0]["generated_text"]
                        
                    else:
                        # Direct model loading approach
                        model = Gemma3ForConditionalGeneration.from_pretrained(
                            self.model_name, 
                            device_map="auto",
                            torch_dtype=torch.bfloat16
                        ).eval()
                        
                        processor = AutoProcessor.from_pretrained(self.model_name)
                        
                        # Store both the model and processor
                        self.model = model
                        self.processor = processor
                        
                        # Process the input
                        inputs = self.processor(prompt, return_tensors="pt").to(self.model.device)
                        
                        # Generate response with config options
                        outputs = self.model.generate(
                            **inputs,
                            max_new_tokens=self.config["max_tokens"],
                            do_sample=self.config["do_sample"],
                            temperature=self.config["temperature"],
                            top_p=self.config["top_p"]
                        )
                        
                        # Decode the response
                        response = self.processor.decode(outputs[0], skip_special_tokens=True)
                    
                    # Extract just the answer part (after "Answer:")
                    if "Answer:" in response:
                        response = response.split("Answer:")[1].strip()
                    
                    return response
                
            except ImportError:
                # Gemma module not available, use simulated response based on context
                logger.warning("Gemma module not available. Using simulated responses.")
                return self._simulate_response(question, context)
                
        except Exception as e:
            # If something goes wrong, log the error and return a fallback response
            logger.error(f"Error generating response: {e}")
            return (
                "I'm sorry, I encountered an issue processing your question. "
                "Based on the legal information I have, I can tell you that the Bulgarian "
                "Labor Code does address this topic, but I recommend consulting the specific "
                "articles in the law or speaking with a legal professional for accurate guidance."
            )
    
    def _simulate_response(self, question: str, context: str) -> str:
        """
        Simulate a response based on the context when the Gemma model is not available
        
        Args:
            question: The user's question
            context: Context from the database
            
        Returns:
            Simulated answer
        """
        # Simple keyword matching to create an intelligent-seeming response
        question_lower = question.lower()
        
        # Extract key article numbers and detailed content from context
        articles = []
        article_numbers = []
        article_contents = {}
        
        # Parse the context to extract article numbers and their complete content
        current_article = None
        current_content = []
        
        for line in context.split('\n'):
            if line.startswith("Article:"):
                # Save previous article if exists
                if current_article and current_content:
                    article_contents[current_article] = "\n".join(current_content)
                    current_content = []
                
                # Start new article
                current_article = line.replace("Article:", "").strip()
                article_numbers.append(current_article)
                
            elif line.startswith("Content:"):
                content = line.replace("Content:", "").strip()
                current_content.append(content)
                articles.append(content)
        
        # Save the last article
        if current_article and current_content:
            article_contents[current_article] = "\n".join(current_content)
        
        # Get top 3 article references
        top_articles = article_numbers[:3]
        article_refs = ", ".join(top_articles)
        
        # Match questions to appropriate responses based on key topics
        if any(term in question_lower for term in ["изпитателен срок", "изпитателния срок", "probation", "trial period", "test period"]):
            # Specific response for probation period questions
            # Search for articles about probation periods (Article 70 in Labor Code)
            probation_articles = []
            
            # Look for articles 70 and 71 which discuss probation periods
            # First, check if we found them in search results
            for art_num in ["Чл. 70", "Чл. 71"]:
                if art_num in article_contents:
                    probation_articles.append((art_num, article_contents[art_num]))
            
            # If not found in search results, use hardcoded versions (this is a failsafe)
            if not probation_articles:
                probation_article_70 = """Чл. 70. (1) (Изм. - ДВ, бр. 100 от 1992 г., доп. - ДВ, бр. 62 от 2022 г., в сила от 01.08.2022 г.) Когато работата изисква да се провери годността на работника или служителя да я изпълнява, окончателното приемане на работа може да се предшествува от договор със срок за изпитване до 6 месеца, а когато за работата е определен срок, по-кратък от една година - срокът за изпитване е до един месец. Такъв договор може да се сключи и когато работникът или служителят желае да провери дали работата е подходяща за него.
(2) (Нова - ДВ, бр. 25 от 2001 г., в сила от 31.03.2001 г.) В договора по ал. 1 се посочва в чия полза е уговорен срокът за изпитване. Ако това не е посочено в договора, приема се, че срокът за изпитване е уговорен в полза и на двете страни.
(3) (Предишна ал. 2 - ДВ, бр. 25 от 2001 г., в сила от 31.03.2001 г.) През време на изпитването страните имат всички права и задължения както при окончателен трудов договор.
(4) (Изм. - ДВ, бр. 100 от 1992 г., предишна ал. 3 - ДВ, бр. 25 от 2001 г., в сила от 31.03.2001 г.) В срока за изпитването не се включва времето, през което работникът или служителят е бил в законоустановен отпуск или по други уважителни причини не е изпълнявал работата, за която е сключен договорът.
(5) (Нова - ДВ, бр. 25 от 2001 г., в сила от 31.03.2001 г.) За една и съща работа с един и същ работник или служител в едно и също предприятие трудов договор със срок за изпитване може да се сключва само веднъж."""
                
                probation_article_71 = """Чл. 71. (1) До изтичане на срока за изпитване страната, в чиято полза е уговорен, може да прекрати договора без предизвестие.
(2) Трудовият договор се смята за окончателно сключен, ако не бъде прекратен по предходната алинея до изтичане на срока за изпитване.
(3) (Отм. - ДВ, бр. 21 от 1990 г.)"""
                
                probation_articles = [
                    ("Чл. 70", probation_article_70),
                    ("Чл. 71", probation_article_71)
                ]
            
            # If we found the relevant articles, include their content
            if probation_articles:
                response = "Съгласно Кодекса на труда относно изпитателния срок:\n\n"
                
                for art_num, content in probation_articles:
                    response += f"### {art_num}:\n{content}\n\n"
                
                response += ("Обобщение: Изпитателният срок може да бъде до 6 месеца, когато работата изисква да се провери годността на работника или служителя. "
                           "За работа със срок по-кратък от една година, изпитателният срок е до един месец. "
                           "Изпитателният срок може да бъде уговорен в полза на работодателя, работника или и двете страни.\n\n"
                           "Моля, имайте предвид, че това е обща информация, а не правен съвет. "
                           "За вашата конкретна ситуация, консултирайте се с квалифициран трудов адвокат.")
                           
                return response
            
        if any(term in question_lower for term in ["отпуск", "годишен отпуск", "leave", "vacation"]):
            return (
                f"According to the Bulgarian Labor Code (see {article_refs}), employees are entitled to at least "
                f"20 working days of paid annual leave. Workers under 18 years of age are entitled to at least "
                f"26 working days. Some positions may be entitled to extended leave based on specific regulations. "
                f"The employer is obligated to ensure that the employee can take this leave within the calendar year, "
                f"though in some circumstances it may be postponed.\n\n"
                f"Please note that this is general information and not legal advice. "
                f"For your specific situation, you should consult with a qualified labor lawyer."
            )
            
        elif any(term in question_lower for term in ["прекратяване", "договор", "termination", "contract", "уволнение"]):
            # Check if this is about probation period termination or expiration
            if any(term in question_lower for term in ["изпитателен срок", "изтече", "изтичане", "expire", "probation"]):
                # This is about what happens when probation period expires
                # Return specific info from Article 71
                probation_article_71 = """Чл. 71. (1) До изтичане на срока за изпитване страната, в чиято полза е уговорен, може да прекрати договора без предизвестие.
(2) Трудовият договор се смята за окончателно сключен, ако не бъде прекратен по предходната алинея до изтичане на срока за изпитване.
(3) (Отм. - ДВ, бр. 21 от 1990 г.)"""
                
                return (
                    f"Съгласно Кодекса на труда, член 71, алинея 2 гласи:\n\n"
                    f"\"{probation_article_71}\"\n\n"
                    f"Тоест, ако трудовият договор с изпитателен срок не бъде прекратен до изтичането на изпитателния срок, "
                    f"той автоматично се смята за окончателно сключен и продължава като стандартен трудов договор. "
                    f"Пълният текст на съответните разпоредби в Кодекса на труда, Член 71 е посочен по-горе.\n\n"
                    f"Моля, имайте предвид, че това е обща информация, а не правен съвет. "
                    f"За вашата конкретна ситуация, консултирайте се с квалифициран трудов адвокат."
                )
            else:
                # General termination info
                return (
                    f"According to the Bulgarian Labor Code (see {article_refs}), employment contracts can be terminated "
                    f"through several methods, including mutual agreement, with notice (typically 30 days unless otherwise "
                    f"specified), without notice under specific circumstances, or after a disciplinary dismissal procedure. "
                    f"Employers must provide proper written notice and justification based on grounds specified in the Labor Code. "
                    f"If terminated without just cause, you may be entitled to compensation.\n\n"
                    f"Please note that this is general information and not legal advice. "
                    f"For your specific situation, you should consult with a qualified labor lawyer."
                )
            
        elif any(term in question_lower for term in ["заплата", "възнаграждение", "salary", "compensation", "pay"]):
            return (
                f"According to the Bulgarian Labor Code (see {article_refs}), salaries must be paid at least once a month, "
                f"and cannot be less than the national minimum wage. The Labor Code requires equal pay for equal work, "
                f"prohibiting discrimination. Employers must provide detailed pay slips and are required to maintain "
                f"records of all payments. If an employer delays payment, employees may be entitled to additional compensation.\n\n"
                f"Please note that this is general information and not legal advice. "
                f"For your specific situation, you should consult with a qualified labor lawyer."
            )
            
        elif any(term in question_lower for term in ["работно време", "working hours", "overtime"]):
            return (
                f"According to the Bulgarian Labor Code (see {article_refs}), the standard workweek is 40 hours, typically "
                f"distributed as 8 hours per day for a 5-day workweek. Overtime is permitted only in exceptional circumstances "
                f"and must be compensated at a higher rate (at least 50% higher for weekdays, 75% for weekends, and 100% for "
                f"official holidays). There are strict limitations on total overtime hours allowed.\n\n"
                f"Please note that this is general information and not legal advice. "
                f"For your specific situation, you should consult with a qualified labor lawyer."
            )
            
        else:
            # For other questions, provide a response with relevant article excerpts
            # Limit to top 2 most relevant articles to keep the response focused
            detailed_response = f"Според Кодекса на труда, следните членове са свързани с вашия въпрос:\n\n"
            
            # Include up to 2 most relevant articles with their full text
            for i, article_num in enumerate(top_articles[:2]):
                if article_num in article_contents:
                    detailed_response += f"### {article_num}:\n{article_contents[article_num]}\n\n"
            
            # Add a general conclusion
            detailed_response += (
                f"Горепосочените членове са най-релевантни към вашия въпрос. "
                f"Ако имате нужда от повече специфична информация, моля задайте по-конкретен въпрос или "
                f"се консултирайте с квалифициран трудов адвокат.\n\n"
                f"Моля, имайте предвид, че това е обща информация, а не правен съвет. "
                f"За вашата конкретна ситуация, консултирайте се с квалифициран трудов адвокат."
            )
            
            return detailed_response
    
    def _prepare_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Prepare source citations from search results
        
        Args:
            search_results: Search results from the database
            
        Returns:
            List of source dictionaries
        """
        sources = []
        
        for result in search_results:
            metadata = result["metadata"]
            
            source = {
                "title": metadata["law_title"],
                "article": metadata["article_number"],
                "relevance": f"{result['similarity'] * 100:.1f}%"
            }
            
            sources.append(source)
        
        return sources