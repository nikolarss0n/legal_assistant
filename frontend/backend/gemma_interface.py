import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GemmaInterface:
    def __init__(self, model_name="google/gemma-3-8b-instruct", quantize="4bit", device=None):
        """
        Initialize the Gemma 3 model.
        
        Args:
            model_name: The name of the model to use.
            quantize: The quantization level to use (None, "4bit", "8bit").
            device: The device to use ("cpu", "cuda", "mps" or None for auto-detect).
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipe = None
        self.quantize = quantize
        
        # Determine device
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
            
        print(f"Using device: {self.device}")
        
        # Load the model
        self._load_model()
        
    def _load_model(self):
        """Load the Gemma 3 model with appropriate quantization."""
        try:
            # Check if model is a local path or Hugging Face model ID
            is_local_path = os.path.exists(self.model_name)
            
            # Load tokenizer - no token needed for local model
            if is_local_path:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            else:
                # Fallback to Hugging Face with token
                hf_token = os.environ.get("HUGGINGFACE_TOKEN")
                if not hf_token:
                    print("Warning: HUGGINGFACE_TOKEN not found, trying to load model without token")
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name,
                    token=hf_token if hf_token else None
                )
            
            # Configure model loading based on quantization
            load_kwargs = {}
            if not is_local_path and os.environ.get("HUGGINGFACE_TOKEN"):
                load_kwargs["token"] = os.environ.get("HUGGINGFACE_TOKEN")
            
            if self.quantize == "4bit":
                load_kwargs.update({
                    "quantization_config": {"load_in_4bit": True},
                    "device_map": "auto"
                })
            elif self.quantize == "8bit":
                load_kwargs.update({
                    "quantization_config": {"load_in_8bit": True},
                    "device_map": "auto"
                })
            else:
                # No quantization
                load_kwargs.update({"device_map": self.device})
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **load_kwargs
            )
            
            # Create pipeline
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer
            )
            
            print(f"Gemma 3 model loaded successfully: {self.model_name}")
            
        except Exception as e:
            print(f"Error loading Gemma 3 model: {e}")
            self.model = None
            self.tokenizer = None
            raise
    
    def generate_response(self, query, articles=None, language="en", conversation_history=None):
        """
        Generate a response using Gemma 3.
        
        Args:
            query: The user's query about labor law.
            articles: List of relevant articles (dicts with number, title, content).
            language: The language to respond in ("en" or "bg").
            conversation_history: Previous messages in the conversation (optional).
        
        Returns:
            Generated response text.
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded properly")
        
        # Prepare context from articles
        context = ""
        if articles:
            for article in articles:
                context += f"Article {article['number']}: {article['title']}\n{article['content']}\n\n"
        
        # Add extended legal information for certain topics
        if any("70" == article["number"] or "71" == article["number"] for article in articles or []):
            # Add extended information about probation periods
            if language == "bg":
                context += "\nДопълнителна информация за изпитателен срок:\n"
                context += "Ако няма изрично писмено споразумение за изпитателен срок, такъв не се счита за уговорен. "
                context += "При неспазване на изпитателния срок, засегнатата страна може да подаде жалба в Инспекцията по труда. "
                context += "Глобите за работодател, който неправомерно прекрати трудов договор през изпитателния срок, могат да достигнат до 15,000 лева. "
                context += "Възможни са и съдебни искове за неправомерно прекратяване на трудовото правоотношение."
            else:
                context += "\nAdditional information about probation periods:\n"
                context += "If there is no explicit written agreement for a probation period, it is not considered agreed upon. "
                context += "In case of non-compliance with the probation period terms, the affected party can file a complaint with the Labor Inspectorate. "
                context += "Fines for an employer who unlawfully terminates an employment contract during the probation period can reach up to 15,000 BGN. "
                context += "Legal claims for wrongful termination of employment are also possible."
        
        # Determine system prompt based on language
        if language == "bg":
            system_prompt = (
                "Ти си професионален асистент за българското трудово право, който може да задава въпроси и да обсъжда сценарии. "
                "Използвай предоставената информация, за да отговориш на въпроса, но също така можеш да задаваш въпроси на потребителя "
                "за да разбереш по-добре ситуацията и да дадеш по-точен съвет. "
                "Ако въпросът е свързан с конкретна ситуация, попитай за детайли. "
                "Обясни правни последици, възможни санкции и следващи стъпки в правния процес. "
                "Отговори на български език."
            )
        else:
            system_prompt = (
                "You are a professional assistant for Bulgarian labor law who can ask questions and discuss scenarios. "
                "Use the provided information to answer the question, but you can also ask the user questions "
                "to better understand their situation and provide more accurate advice. "
                "If the question relates to a specific situation, ask for details. "
                "Explain legal consequences, possible sanctions, and next steps in the legal process. "
                "Answer in English."
            )
        
        # Create prompt with context
        if context:
            if language == "bg":
                prompt = (
                    f"Използвай следната информация, за да отговориш на БЪЛГАРСКИ ЕЗИК:\n\n{context}\n\n"
                    f"Въпрос на потребителя: {query}\n\n"
                    f"Структурирай отговора си В СЛЕДНИЯ ТОЧЕН ФОРМАТ с 4 ясно разделени секции (ЗАДЪЛЖИТЕЛНО използвай точно тези заглавия):\n\n"
                    f"СЕКЦИЯ 1: Кратко изречение, което казва кои членове от Кодекса на труда са приложими, например: \"Намерих следните приложими членове от Кодекса на труда: Член 70, Член 71\".\n\n"
                    f"СЕКЦИЯ 2: Обобщение на информацията от тези членове, което отговаря на въпроса на потребителя.\n\n"
                    f"СЕКЦИЯ 3: Точният законов текст от приложимите членове, като използваш термина \"Член\" вместо \"Article\" и запази оригиналния текст без обобщения.\n\n"
                    f"СЕКЦИЯ 4: Обяснение на последиците от неспазване на тези правни разпоредби, включително възможни глоби, санкции или съдебни производства. Също така, опиши опции за предотвратяване на проблеми и алтернативни подходи. Накрая, задай поне един въпрос към потребителя, за да разбереш повече за ситуацията.\n\n"
                    f"ВАЖНО: Напиши целия отговор НА БЪЛГАРСКИ ЕЗИК и използвай ТОЧНО форматирането с СЕКЦИЯ 1:, СЕКЦИЯ 2:, СЕКЦИЯ 3:, СЕКЦИЯ 4: за разделяне на секциите."
                )
            else:
                prompt = (
                    f"Use the following information to answer:\n\n{context}\n\n"
                    f"User question: {query}\n\n"
                    f"Structure your response in the following format with 4 clearly separated sections:\n\n"
                    f"SECTION 1: A brief sentence stating which articles from the Labor Code are applicable, for example: \"I found the following applicable articles from the Labor Code: Article 70, Article 71\".\n\n"
                    f"SECTION 2: A summary of the information from these articles that answers the user's question.\n\n"
                    f"SECTION 3: The exact legal text from the applicable articles, using the original wording without summarization.\n\n"
                    f"SECTION 4: An explanation of the consequences of not following these legal provisions, including possible fines, sanctions, or legal proceedings. Also, describe options for preventing problems and alternative approaches. Finally, ask at least one question to the user to better understand their situation."
                )
        else:
            if language == "bg":
                prompt = (
                    f"Въпрос на потребителя: {query}\n\n"
                    f"Отговори, че не разполагаш с пълна информация по този въпрос и "
                    f"посъветвай потребителя да се консултира с правен експерт. "
                    f"Същевременно, попитай потребителя дали има конкретен аспект на трудовото законодателство, "
                    f"който го интересува, за да можеш да му дадеш по-точни насоки."
                )
            else:
                prompt = (
                    f"User question: {query}\n\n"
                    f"Answer that you don't have complete information on this topic and "
                    f"advise the user to consult with a legal expert. "
                    f"At the same time, ask the user if there's a specific aspect of labor law "
                    f"they're interested in, so you can provide more precise guidance."
                )
        
        # Generate response
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        chat = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        outputs = self.pipe(
            chat,
            max_new_tokens=1024,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            return_full_text=False
        )
        
        response = outputs[0]["generated_text"]
        return response.strip()
    
    def detect_language(self, text):
        """Detect if the text is in Bulgarian or English."""
        # Simple heuristic: if there are Cyrillic characters, assume Bulgarian
        # Convert to lowercase to handle more characters
        text_lower = text.lower()
        
        # Count Cyrillic characters
        cyrillic_count = sum(1 for c in text_lower if ord(c) > 1024 and ord(c) < 1280)
        
        # If more than 2 Cyrillic characters, consider it Bulgarian
        return "bg" if cyrillic_count > 2 else "en"