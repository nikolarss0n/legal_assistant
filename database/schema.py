"""
Database schema for the legal assistant application.
Defines the structure of our hybrid database.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class LegalArticle:
    """Represents a single article from a legal document"""
    id: str  # Unique identifier for the article
    law_id: str  # ID of the parent law
    number: str  # Article number (e.g., "Art. 12")
    content: str  # Full text content of the article
    embedding_id: Optional[str] = None  # ID in the vector store


@dataclass
class LegalDocument:
    """Represents a legal document (e.g., a law, regulation, etc.)"""
    id: str  # Unique identifier for the document
    title: str  # Title of the legal document
    document_type: str  # Type (e.g., "law", "regulation", "decree")
    source_url: str  # Original URL where document was scraped from
    date_published: Optional[datetime] = None  # When the law was published/enacted
    date_modified: Optional[datetime] = None  # When the law was last modified
    date_scraped: datetime = datetime.now()  # When this was scraped
    is_current: bool = True  # Whether this is the current version
    articles: List[LegalArticle] = None  # The articles contained in this document
    
    # Metadata fields for filtering
    tags: List[str] = None  # Tags for categorization (e.g., "labor", "tax", "criminal")
    category: Optional[str] = None  # Main category
    subcategory: Optional[str] = None  # Subcategory


@dataclass
class LegalAmendment:
    """Represents an amendment to a legal document"""
    id: str  # Unique identifier for the amendment
    law_id: str  # ID of the law being amended
    amendment_date: datetime  # When the amendment was enacted
    description: str  # Description of what changed
    affected_articles: List[str]  # IDs of affected articles
    amendment_text: str  # The full text of the amendment
    source_url: str  # Original URL where amendment was scraped from


@dataclass
class VectorDBConfig:
    """Configuration for the vector database"""
    collection_name: str = "legal_articles"
    embedding_dimension: int = 768  # For default embeddings
    distance_metric: str = "cosine"
    

# Schema for SQL tables
SQL_SCHEMA = {
    "legal_documents": """
        CREATE TABLE IF NOT EXISTS legal_documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            source_url TEXT NOT NULL,
            date_published TEXT,
            date_modified TEXT,
            date_scraped TEXT NOT NULL,
            is_current BOOLEAN NOT NULL DEFAULT TRUE,
            category TEXT,
            subcategory TEXT
        )
    """,
    
    "legal_articles": """
        CREATE TABLE IF NOT EXISTS legal_articles (
            id TEXT PRIMARY KEY,
            law_id TEXT NOT NULL,
            number TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding_id TEXT,
            FOREIGN KEY (law_id) REFERENCES legal_documents (id)
        )
    """,
    
    "document_tags": """
        CREATE TABLE IF NOT EXISTS document_tags (
            document_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            PRIMARY KEY (document_id, tag),
            FOREIGN KEY (document_id) REFERENCES legal_documents (id)
        )
    """,
    
    "legal_amendments": """
        CREATE TABLE IF NOT EXISTS legal_amendments (
            id TEXT PRIMARY KEY,
            law_id TEXT NOT NULL,
            amendment_date TEXT NOT NULL,
            description TEXT NOT NULL,
            amendment_text TEXT NOT NULL,
            source_url TEXT NOT NULL,
            FOREIGN KEY (law_id) REFERENCES legal_documents (id)
        )
    """,
    
    "amendment_affected_articles": """
        CREATE TABLE IF NOT EXISTS amendment_affected_articles (
            amendment_id TEXT NOT NULL,
            article_id TEXT NOT NULL,
            PRIMARY KEY (amendment_id, article_id),
            FOREIGN KEY (amendment_id) REFERENCES legal_amendments (id),
            FOREIGN KEY (article_id) REFERENCES legal_articles (id)
        )
    """
}