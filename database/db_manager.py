"""
Database manager for the legal assistant application.
Handles interactions with both the vector database and SQL database.
"""

import os
import uuid
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings

from .schema import (
    LegalDocument,
    LegalArticle,
    LegalAmendment,
    VectorDBConfig,
    SQL_SCHEMA
)


class HybridDatabaseManager:
    """
    Manages interactions with both vector database and SQL database.
    Provides a unified interface for storing and retrieving legal data.
    """
    
    def __init__(
        self,
        db_path: str = "../data/legal_db.sqlite",
        vector_db_path: str = "../data/vector_db",
        vector_config: VectorDBConfig = None
    ):
        """
        Initialize the database manager
        
        Args:
            db_path: Path to the SQLite database file
            vector_db_path: Path to the ChromaDB directory
            vector_config: Configuration for the vector database
        """
        self.db_path = db_path
        self.vector_db_path = vector_db_path
        self.vector_config = vector_config or VectorDBConfig()
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(vector_db_path, exist_ok=True)
        
        # Initialize databases
        self._init_sql_db()
        self._init_vector_db()
    
    def _init_sql_db(self):
        """Initialize the SQL database with the schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables from schema
        for table_name, create_statement in SQL_SCHEMA.items():
            cursor.execute(create_statement)
        
        conn.commit()
        conn.close()
    
    def _init_vector_db(self):
        """Initialize the vector database"""
        self.chroma_client = chromadb.PersistentClient(
            path=self.vector_db_path,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Create collection if it doesn't exist
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.vector_config.collection_name
            )
            print(f"Using existing collection: {self.vector_config.collection_name}")
        except Exception as e:
            print(f"Collection error: {e}")
            print(f"Creating new collection: {self.vector_config.collection_name}")
            # Collection doesn't exist, create it
            self.collection = self.chroma_client.create_collection(
                name=self.vector_config.collection_name,
                metadata={"hnsw:space": self.vector_config.distance_metric}
            )
        
        # Initialize a simple embedding model
        from langchain_core.embeddings import Embeddings
        
        class SimpleEmbeddings(Embeddings):
            """A simple embedding model that returns random vectors."""
            
            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                """Embed a list of documents using a very basic method."""
                import numpy as np
                # Use a simple hash-based approach to generate vectors
                # This is not a good embedding model, but it allows us to test the system
                return [self._hash_embed(text) for text in texts]
            
            def embed_query(self, text: str) -> list[float]:
                """Embed a query using a very basic method."""
                import numpy as np
                return self._hash_embed(text)
            
            def _hash_embed(self, text: str) -> list[float]:
                """Create a simple hash-based embedding."""
                import numpy as np
                # Use a simple hash function to convert text to a vector
                # This is NOT a good embedding model, just for testing
                np.random.seed(sum(ord(c) for c in text))
                # Return a vector of size 768 (common embedding dimension)
                return list(np.random.uniform(-1, 1, 768).astype(float))
        
        self.embeddings = SimpleEmbeddings()
    
    def add_document(self, document: LegalDocument) -> str:
        """
        Add a legal document to both databases
        
        Args:
            document: The legal document to add
            
        Returns:
            The ID of the added document
        """
        if not document.id:
            document.id = str(uuid.uuid4())
        
        # Connect to SQL database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert the document
            cursor.execute(
                """
                INSERT INTO legal_documents 
                (id, title, document_type, source_url, date_published, 
                date_modified, date_scraped, is_current, category, subcategory)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.id,
                    document.title,
                    document.document_type,
                    document.source_url,
                    document.date_published.isoformat() if document.date_published else None,
                    document.date_modified.isoformat() if document.date_modified else None,
                    document.date_scraped.isoformat(),
                    document.is_current,
                    document.category,
                    document.subcategory
                )
            )
            
            # Insert tags
            if document.tags:
                tag_values = [(document.id, tag) for tag in document.tags]
                cursor.executemany(
                    "INSERT INTO document_tags (document_id, tag) VALUES (?, ?)",
                    tag_values
                )
            
            # Process articles
            if document.articles:
                for article in document.articles:
                    if not article.id:
                        article.id = str(uuid.uuid4())
                    
                    article.law_id = document.id
                    
                    # Generate embedding and add to vector database
                    embedding = self.embeddings.embed_query(article.content)
                    
                    # Add to vector DB
                    article.embedding_id = f"{article.id}_embedding"
                    self.collection.add(
                        ids=[article.embedding_id],
                        embeddings=[embedding],
                        metadatas=[{
                            "article_id": article.id,
                            "law_id": document.id,
                            "article_number": article.number,
                            "law_title": document.title
                        }],
                        documents=[article.content]
                    )
                    
                    # Add to SQL database
                    cursor.execute(
                        """
                        INSERT INTO legal_articles
                        (id, law_id, number, content, embedding_id)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            article.id,
                            article.law_id,
                            article.number,
                            article.content,
                            article.embedding_id
                        )
                    )
            
            conn.commit()
            return document.id
            
        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            conn.close()
    
    def add_amendment(self, amendment: LegalAmendment) -> str:
        """
        Add a legal amendment to the database
        
        Args:
            amendment: The amendment to add
            
        Returns:
            The ID of the added amendment
        """
        if not amendment.id:
            amendment.id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert the amendment
            cursor.execute(
                """
                INSERT INTO legal_amendments
                (id, law_id, amendment_date, description, amendment_text, source_url)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    amendment.id,
                    amendment.law_id,
                    amendment.amendment_date.isoformat(),
                    amendment.description,
                    amendment.amendment_text,
                    amendment.source_url
                )
            )
            
            # Insert affected articles
            if amendment.affected_articles:
                affected_values = [
                    (amendment.id, article_id) 
                    for article_id in amendment.affected_articles
                ]
                cursor.executemany(
                    """
                    INSERT INTO amendment_affected_articles
                    (amendment_id, article_id) VALUES (?, ?)
                    """,
                    affected_values
                )
            
            conn.commit()
            return amendment.id
            
        except Exception as e:
            conn.rollback()
            raise e
        
        finally:
            conn.close()
    
    def search_similar(
        self, 
        query: str, 
        n_results: int = 5,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for articles similar to the query
        
        Args:
            query: The search query
            n_results: Number of results to return
            filters: Metadata filters to apply
            
        Returns:
            List of article dictionaries
        """
        # Generate embedding for the query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search vector database
        search_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        
        # Format results
        results = []
        for i in range(len(search_results["ids"][0])):
            result = {
                "content": search_results["documents"][0][i],
                "metadata": search_results["metadatas"][0][i],
                "similarity": 1 - search_results["distances"][0][i] 
                # Convert distance to similarity score
            }
            results.append(result)
        
        # If filters are provided, apply SQL filtering
        if filters:
            filtered_results = self._apply_sql_filters(results, filters)
            return filtered_results
        
        return results
    
    def _apply_sql_filters(
        self, 
        vector_results: List[Dict[str, Any]], 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply SQL filters to vector search results
        
        Args:
            vector_results: Results from vector search
            filters: Filters to apply
            
        Returns:
            Filtered results
        """
        if not filters or not vector_results:
            return vector_results
        
        # Extract article IDs for SQL filtering
        article_ids = [r["metadata"]["article_id"] for r in vector_results]
        placeholders = ",".join(["?"] * len(article_ids))
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Build SQL query based on filters
            query = f"""
                SELECT la.id as article_id, la.content, la.number, 
                       ld.id as law_id, ld.title, ld.document_type,
                       ld.date_published, ld.category, ld.subcategory
                FROM legal_articles la
                JOIN legal_documents ld ON la.law_id = ld.id
                LEFT JOIN document_tags dt ON ld.id = dt.document_id
                WHERE la.id IN ({placeholders})
            """
            
            params = list(article_ids)
            where_clauses = []
            
            # Add filter conditions
            if "document_type" in filters:
                where_clauses.append("ld.document_type = ?")
                params.append(filters["document_type"])
            
            if "category" in filters:
                where_clauses.append("ld.category = ?")
                params.append(filters["category"])
            
            if "tags" in filters:
                placeholders = ",".join(["?"] * len(filters["tags"]))
                where_clauses.append(f"dt.tag IN ({placeholders})")
                params.extend(filters["tags"])
            
            if "date_after" in filters:
                where_clauses.append("ld.date_published >= ?")
                params.append(filters["date_after"])
            
            if "date_before" in filters:
                where_clauses.append("ld.date_published <= ?")
                params.append(filters["date_before"])
            
            # Add WHERE clauses if any
            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)
            
            # Group to handle multiple tags
            query += " GROUP BY la.id"
            
            # Execute query
            cursor.execute(query, params)
            sql_results = cursor.fetchall()
            
            # Convert to dictionaries
            sql_results_dict = {row["article_id"]: dict(row) for row in sql_results}
            
            # Merge vector and SQL results
            merged_results = []
            for result in vector_results:
                article_id = result["metadata"]["article_id"]
                if article_id in sql_results_dict:
                    # Add SQL metadata to result
                    result["sql_metadata"] = sql_results_dict[article_id]
                    merged_results.append(result)
            
            return merged_results
            
        finally:
            conn.close()
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by its ID
        
        Args:
            document_id: The ID of the document to retrieve
            
        Returns:
            Document data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get document
            cursor.execute(
                """
                SELECT * FROM legal_documents
                WHERE id = ?
                """,
                (document_id,)
            )
            document = cursor.fetchone()
            
            if not document:
                return None
            
            document_dict = dict(document)
            
            # Get tags
            cursor.execute(
                """
                SELECT tag FROM document_tags
                WHERE document_id = ?
                """,
                (document_id,)
            )
            tags = [row["tag"] for row in cursor.fetchall()]
            document_dict["tags"] = tags
            
            # Get articles
            cursor.execute(
                """
                SELECT * FROM legal_articles
                WHERE law_id = ?
                """,
                (document_id,)
            )
            articles = [dict(row) for row in cursor.fetchall()]
            document_dict["articles"] = articles
            
            return document_dict
            
        finally:
            conn.close()
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an article by its ID
        
        Args:
            article_id: The ID of the article to retrieve
            
        Returns:
            Article data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                SELECT la.*, ld.title as law_title, ld.document_type, 
                       ld.date_published, ld.category, ld.subcategory
                FROM legal_articles la
                JOIN legal_documents ld ON la.law_id = ld.id
                WHERE la.id = ?
                """,
                (article_id,)
            )
            article = cursor.fetchone()
            
            if not article:
                return None
            
            return dict(article)
            
        finally:
            conn.close()
    
    def import_from_json(self, json_file_path: str):
        """
        Import data from a JSON file (as produced by the scraper)
        
        Args:
            json_file_path: Path to the JSON file
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for law_data in data:
            # Skip laws with errors
            if "error" in law_data:
                continue
            
            # Create LegalDocument
            # Try to parse date_published, use current date if it fails
            date_published = datetime.now()
            date_scraped = datetime.now()
            try:
                if "scraped_date" in law_data:
                    date_scraped = datetime.fromisoformat(law_data["scraped_date"])
            except Exception as e:
                print(f"Error parsing scraped_date: {e}")
                
            document = LegalDocument(
                id=str(uuid.uuid4()),
                title=law_data.get("title", "Unknown"),
                document_type="law",  # Assuming these are laws
                source_url=law_data.get("url", ""),
                date_published=date_published,
                date_scraped=date_scraped,
                tags=["labor"],  # Adding a default tag
                category="labor",  # Default category
                articles=[]
            )
            
            # Create LegalArticles
            for article_data in law_data.get("articles", []):
                article = LegalArticle(
                    id=str(uuid.uuid4()),
                    law_id=document.id,  # Will be filled in by add_document
                    number=article_data.get("number", "Unknown"),
                    content=article_data.get("content", "")
                )
                document.articles.append(article)
            
            # Add to database
            self.add_document(document)
            
    def clear_databases(self):
        """Clear both databases (for testing purposes)"""
        # Clear vector database
        try:
            self.chroma_client.delete_collection(self.vector_config.collection_name)
            self._init_vector_db()
        except Exception as e:
            print(f"Error clearing vector database: {e}")
        
        # Clear SQL database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Drop all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                if table_name != "sqlite_sequence":
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            conn.commit()
            
            # Recreate tables
            self._init_sql_db()
            
        except Exception as e:
            conn.rollback()
            print(f"Error clearing SQL database: {e}")
            
        finally:
            conn.close()