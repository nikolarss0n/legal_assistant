# Integrating Gemma 3 with the Bulgarian Labor Law Assistant

This guide explains how to integrate Google's Gemma 3 LLM with the Bulgarian Labor Law Assistant backend.

## Prerequisites

- Python 3.8+
- Access to the Labor Law Assistant backend code
- Hugging Face account (for accessing Gemma 3 models)

## Steps for Integrating Gemma 3

### 1. Install Required Packages

```bash
pip install transformers torch accelerate bitsandbytes sentencepiece
```

### 2. Download and Set Up Gemma 3 Model

Before using Gemma 3, you need to accept the model license on Hugging Face. Visit:
https://huggingface.co/google/gemma-3-8b-instruct

Then create a `.env` file in your backend's root directory with your Hugging Face token:

```
HUGGINGFACE_TOKEN=your_huggingface_token
```

### 3. Create a Gemma Interface Module

Create a file called `gemma_interface.py` in your backend:

```python
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
            # Set HF token
            hf_token = os.environ.get("HUGGINGFACE_TOKEN")
            if not hf_token:
                raise ValueError("HUGGINGFACE_TOKEN not found in environment")
                
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                token=hf_token
            )
            
            # Configure model loading based on quantization
            load_kwargs = {"token": hf_token}
            
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
    
    def generate_response(self, query, articles=None, language="en"):
        """
        Generate a response using Gemma 3.
        
        Args:
            query: The user's query about labor law.
            articles: List of relevant articles (dicts with number, title, content).
            language: The language to respond in ("en" or "bg").
        
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
        
        # Determine system prompt based on language
        if language == "bg":
            system_prompt = (
                "Ти си професионален асистент за българското трудово право. "
                "Използвай само предоставената информация, за да отговориш на въпроса. "
                "Отговори на български език."
            )
        else:
            system_prompt = (
                "You are a professional assistant for Bulgarian labor law. "
                "Use only the provided information to answer the question. "
                "Answer in English."
            )
        
        # Create prompt with context
        if context:
            if language == "bg":
                prompt = (
                    f"Използвай само следната информация, за да отговориш:\n\n{context}\n\n"
                    f"Въпрос: {query}\n\n"
                    f"Отговори точно и ясно, базирайки се само на предоставената информация. "
                    f"Не измисляй факти."
                )
            else:
                prompt = (
                    f"Use only the following information to answer:\n\n{context}\n\n"
                    f"Question: {query}\n\n"
                    f"Answer accurately based only on the provided information. "
                    f"Do not make up facts."
                )
        else:
            if language == "bg":
                prompt = (
                    f"Въпрос: {query}\n\n"
                    f"Отговори, че не разполагаш с достатъчно информация по този въпрос и "
                    f"посъветвай потребителя да се консултира с правен експерт."
                )
            else:
                prompt = (
                    f"Question: {query}\n\n"
                    f"Answer that you don't have enough information on this topic and "
                    f"advise the user to consult with a legal expert."
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
        return "bg" if any(ord(c) > 1024 and ord(c) < 1280 for c in text) else "en"
```

### 4. Update Your Legal Query Module

Modify your main query handler to use Gemma:

```python
from gemma_interface import GemmaInterface
from db_manager import DBManager  # Your existing database manager
import os

# Initialize components
db = DBManager()  # Your existing database manager
gemma = GemmaInterface(quantize="4bit")  # Use 8bit for better performance on lower-end machines

def answer_legal_query(query):
    """
    Process a legal query and return answer with relevant articles.
    
    Args:
        query: The user's question about labor law
        
    Returns:
        Dict with answer and relevant articles
    """
    # Detect language
    language = gemma.detect_language(query)
    
    # Search for relevant articles
    articles = db.search_articles(query)
    
    if not articles:
        # No relevant articles found
        if language == "bg":
            answer = "Съжалявам, не успях да намеря информация по този въпрос в Кодекса на труда. Моля, консултирайте се с правен експерт."
        else:
            answer = "I'm sorry, I couldn't find information on this topic in the Labor Code. Please consult with a legal expert."
        return {"answer": answer, "articles": []}
    
    # Generate response with Gemma 3
    try:
        answer = gemma.generate_response(query, articles, language)
    except Exception as e:
        print(f"Error generating response with Gemma: {e}")
        # Fallback message
        if language == "bg":
            answer = f"Намерих следните членове от Кодекса на труда, които може да са свързани с вашия въпрос."
        else:
            answer = f"I found the following articles from the Labor Code that might be relevant to your question."
    
    return {
        "answer": answer,
        "articles": articles
    }
```

### 5. Create a REST API Endpoint

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from legal_query import answer_legal_query

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    result = answer_legal_query(data['query'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 6. Handling Model Unavailability

If you can't use Gemma 3 due to hardware constraints or token issues, consider these alternatives:

1. **Use a smaller model**: Try Gemma 3 2B instead of 8B
2. **Use GGUF or other optimized formats**: These offer better performance on lower-end hardware
3. **Implement a template-based fallback**: Generate responses based on templates when the model isn't available

### 7. Performance Considerations

- For 8B parameter models, you'll need at least 16GB RAM
- With 4-bit quantization, you can run on systems with 8GB RAM
- When using GPU:
  - CUDA: 8GB+ VRAM recommended
  - MPS (Apple Silicon): Works well even on base M1/M2 Macs

## Integration with the Frontend

The frontend already has the necessary components to connect to this backend:

1. Update the API URL in `src/config.ts` to point to your backend
2. Uncomment the line `const response = await searchLegalInfo(text);` in `App.tsx`
3. Comment out the simulation line above it

## Testing

1. Run the backend server first: `python app.py`
2. Then start the frontend: `npm run dev` 
3. Enter questions in Bulgarian or English to test the system

## Conclusion

With these changes, the Bulgarian Labor Law Assistant will now use Gemma 3 to generate high-quality, context-aware responses based on the Bulgarian Labor Code. The system automatically detects the query language and responds in the same language.