"""
Database module for the legal assistant application.
"""

from .db_manager import HybridDatabaseManager
from .schema import (
    LegalDocument,
    LegalArticle,
    LegalAmendment,
    VectorDBConfig
)

__all__ = [
    'HybridDatabaseManager',
    'LegalDocument',
    'LegalArticle',
    'LegalAmendment',
    'VectorDBConfig'
]