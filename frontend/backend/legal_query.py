import os
from gemma_interface import GemmaInterface
from db_manager import DBManager

# Initialize components
db = DBManager()  # Database manager
gemma = None  # Will initialize on-demand

def get_gemma():
    """Lazy load the Gemma model."""
    global gemma
    if gemma is None:
        try:
            # Use the gemma-3-model folder in the root directory
            default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "gemma-3-model")
            local_model_path = os.environ.get("GEMMA_PATH", default_path)
            print(f"Loading model from: {local_model_path}")
            
            gemma = GemmaInterface(
                model_name=local_model_path,
                quantize="4bit"  # Use 8bit for better performance on lower-end machines
            )
        except Exception as e:
            print(f"Error initializing Gemma: {e}")
    return gemma

def answer_legal_query(query):
    """
    Process a legal query and return answer with relevant articles.
    
    Args:
        query: The user's question about labor law
        
    Returns:
        Dict with answer and relevant articles
    """
    # Get language
    language = "en"  # Default
    gemma_instance = get_gemma()
    if gemma_instance:
        language = gemma_instance.detect_language(query)
    
    # Search for relevant articles
    articles = db.search_articles(query)
    
    # Convert article representation for Bulgarian responses
    if language == "bg" and articles:
        for article in articles:
            # Change "Article" to "Член" in titles for Bulgarian responses
            if article.get('title_en'):
                # If there's already an English title stored separately, we're good
                pass
            else:
                # Store the English title before changing it
                article['title_en'] = article['title']
                # For Bulgarian responses, use original Bulgarian title
                # No change needed since titles are already in Bulgarian in the database
            
            # Change "number" representation to have "Член" prefix
            if not article.get('display_number'):
                article['display_number'] = f"Член {article['number']}"
    
    if not articles:
        # No relevant articles found
        if language == "bg":
            answer = "Съжалявам, не успях да намеря информация по този въпрос в Кодекса на труда. Моля, консултирайте се с правен експерт."
        else:
            answer = "I'm sorry, I couldn't find information on this topic in the Labor Code. Please consult with a legal expert."
        return {"answer": answer, "articles": []}
    
    # Generate response with Gemma 3
    if gemma_instance:
        try:
            answer = gemma_instance.generate_response(query, articles, language)
        except Exception as e:
            print(f"Error generating response with Gemma: {e}")
            # Fallback message
            if language == "bg":
                answer = f"Намерих следните членове от Кодекса на труда, които може да са свързани с вашия въпрос."
            else:
                answer = f"I found the following articles from the Labor Code that might be relevant to your question."
    else:
        # Fallback if Gemma is not available
        articles_list_bg = ', '.join([f'чл. {a["number"]}' for a in articles])
        articles_list_en = ', '.join([f'Article {a["number"]}' for a in articles])
        
        if language == "bg":
            answer = f"Намерих следните членове от Кодекса на труда по вашия въпрос: {articles_list_bg}"
        else:
            answer = f"I found these relevant articles from the Labor Code: {articles_list_en}"
    
    return {
        "answer": answer,
        "articles": articles
    }