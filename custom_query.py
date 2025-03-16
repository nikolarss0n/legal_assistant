#!/usr/bin/env python3
"""
Custom query script for the labor law database.
"""

import sys
from pathlib import Path
import sqlite3
from database import HybridDatabaseManager

def run_sql_query(db_path, query):
    """Run a direct SQL query on the database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    # Setup paths
    data_dir = Path("data")
    db_path = data_dir / "legal_db.sqlite"
    vector_db_path = data_dir / "vector_db"
    
    # 1. Direct SQL Query Example
    print("=== SQL QUERY EXAMPLES ===")
    
    # Count the number of articles
    result = run_sql_query(str(db_path), "SELECT COUNT(*) as count FROM legal_articles")
    print(f"Number of articles in the database: {result[0]['count']}")
    
    # Get a specific article by number
    article_number = "Чл. 1"  # Looking for Article 1
    result = run_sql_query(
        str(db_path), 
        f"SELECT * FROM legal_articles WHERE number = '{article_number}'"
    )
    
    if result:
        print(f"\nArticle {article_number} found:")
        print(f"Content: {result[0]['content'][:200]}...")
    else:
        print(f"\nArticle {article_number} not found")
    
    # 2. Vector Search Example
    print("\n=== VECTOR SEARCH EXAMPLE ===")
    
    # Initialize the database manager
    db_manager = HybridDatabaseManager(
        db_path=str(db_path),
        vector_db_path=str(vector_db_path)
    )
    
    # Perform a semantic search
    query = "трудов договор срок"  # "employment contract term"
    results = db_manager.search_similar(query, n_results=3)
    
    print(f"Search for '{query}' returned {len(results)} results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Similarity: {result['similarity']:.2f}):")
        print(f"Law: {result['metadata']['law_title']}")
        print(f"Article: {result['metadata']['article_number']}")
        print(f"Content snippet: {result['content'][:150]}...")

if __name__ == "__main__":
    main()