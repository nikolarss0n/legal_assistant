import os
import json

class DBManager:
    def __init__(self, db_file="labor_law_db.json"):
        """Initialize the database manager."""
        self.db_file = db_file
        self.articles = self._load_articles()
        
    def _load_articles(self):
        """Load articles from the database file."""
        # For demonstration, we'll create a simple JSON structure if it doesn't exist
        if not os.path.exists(self.db_file):
            articles = [
                {
                    "number": "70",
                    "title": "Изпитателен срок",
                    "content": "Страните по трудовия договор могат да уговарят изпитателен срок в полза на двете страни, през който работникът или служителят да провери дали работата е подходяща за него, а работодателят да провери годността на работника или служителя за изпълнението й. Такава уговорка е валидна само ако е била изразена писмено. За длъжности, определяни от работодателя, изпитателният срок е в полза на работодателя. В тези случаи работникът или служителят се счита за правоспособен за позицията, ако не му бъде връчено предизвестие за прекратяване на трудовия договор преди изтичането на изпитателния срок."
                },
                {
                    "number": "71",
                    "title": "Срок на изпитването",
                    "content": "Изпитателният срок не може да надвишава 6 месеца. Ако в договора не е уговорен по-кратък срок, счита се, че изпитателният срок е 6 месеца. За срочните трудови договори изпитателният срок следва да е пропорционален на срока на договора. През времето на изпитателния срок страните имат всички права и задължения както при окончателен трудов договор."
                },
                {
                    "number": "155",
                    "title": "Право на платен годишен отпуск",
                    "content": "Всеки работник или служител има право на платен годишен отпуск. При постъпване на работа за първи път работникът или служителят може да използва платения си годишен отпуск, когато придобие най-малко 8 месеца трудов стаж. При прекратяване на трудовото правоотношение преди придобиването на 8 месеца трудов стаж работникът или служителят има право на обезщетение за неизползван платен годишен отпуск."
                },
                {
                    "number": "156",
                    "title": "Размер на платения годишен отпуск",
                    "content": "Минималният размер на основния платен годишен отпуск е 20 работни дни. Някои категории работници и служители в зависимост от особения характер на работата имат право на удължен платен годишен отпуск, в който е включен отпускът по предходната алинея. Категориите работници и служители и минималният размер на този отпуск се определят от Министерския съвет."
                },
                {
                    "number": "242",
                    "title": "Право на трудово възнаграждение",
                    "content": "За изпълнение на трудовите си задължения работникът или служителят има право на трудово възнаграждение. Министерският съвет определя минималната работна заплата за страната. Трудовото възнаграждение се изплаща в пари. Допълнителни трудови възнаграждения могат да се уговарят в колективен трудов договор или в индивидуалния трудов договор."
                },
                {
                    "number": "245",
                    "title": "Изплащане на трудово възнаграждение",
                    "content": "Трудовото възнаграждение се изплаща в пари. Трудовото възнаграждение се изплаща авансово или окончателно всеки месец на два пъти, доколкото не е уговорено друго. Трудовото възнаграждение се изплаща лично на работника или служителя по ведомост или срещу разписка или по писмено искане на работника или служителя на негови близки."
                },
                {
                    "number": "125",
                    "title": "Основни задължения на работника или служителя",
                    "content": "Работникът или служителят е длъжен да изпълнява работата, за която се е уговорил, и да спазва установената трудова дисциплина, да работи добросъвестно и да спазва техническите и технологичните правила, да пази имуществото на работодателя и да бъде лоялен към предприятието, в което работи, да пази доброто име на предприятието, да спазва правилата за здравословни и безопасни условия на труд, да изпълнява и всички други задължения, които произтичат от нормативен акт, от колективен трудов договор, от трудовия договор и от характера на работата."
                }
            ]
            
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            return articles
        else:
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading articles from database: {e}")
                return []
    
    def _get_word_frequency(self, text, query_words):
        """Count how many query words are in the text."""
        text_lower = text.lower()
        count = 0
        for word in query_words:
            if word in text_lower:
                count += 1
        return count
    
    def search_articles(self, query):
        """
        Search for articles related to the query.
        
        Args:
            query: The user's query about labor law
            
        Returns:
            List of relevant articles (dicts with number, title, content)
        """
        query_lower = query.lower()
        query_words = [word for word in query_lower.split() if len(word) > 3]
        
        # General queries about articles or code sections
        if "член" in query_lower or "article" in query_lower or "кодекс" in query_lower or "code" in query_lower:
            # Return a representative sample of articles
            article_numbers = ["70", "125", "155", "242"]
            sample_articles = [article for article in self.articles if article["number"] in article_numbers]
            if sample_articles:
                return sample_articles[:2]  # Return just a couple of examples
        
        # Special case for "задължения" (obligations)
        if "задължен" in query_lower or "задължения" in query_lower or "obligations" in query_lower or "duties" in query_lower:
            return [article for article in self.articles if article["number"] == "125"]
        
        # Special case for "изпитателен срок" (probation period)
        if "изпитателен" in query_lower or "probation" in query_lower or "trial" in query_lower or "срок" in query_lower:
            return [article for article in self.articles if article["number"] in ["70", "71"]]
        
        # Special case for "отпуск" (leave)
        if "отпуск" in query_lower or "почивка" in query_lower or "leave" in query_lower or "vacation" in query_lower:
            return [article for article in self.articles if article["number"] in ["155", "156"]]
        
        # Special case for "заплата" (salary)
        if "заплата" in query_lower or "възнаграждение" in query_lower or "salary" in query_lower or "payment" in query_lower or "money" in query_lower:
            return [article for article in self.articles if article["number"] in ["242", "245"]]
        
        # Check for specific article numbers
        for word in query_lower.split():
            if word.isdigit() and 1 <= int(word) <= 500:  # Assuming Labor Code has articles numbered 1-500
                article_number = word
                matching_articles = [article for article in self.articles if article["number"] == article_number]
                if matching_articles:
                    return matching_articles
        
        # Default: search by word frequency
        results = []
        for article in self.articles:
            combined_text = f"{article['title']} {article['content']}"
            frequency = self._get_word_frequency(combined_text, query_words)
            if frequency > 0:
                results.append((article, frequency))
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        if results:
            return [article for article, _ in results[:2]]
        
        # If no specific match, return articles about worker obligations as a default
        return [article for article in self.articles if article["number"] == "125"]