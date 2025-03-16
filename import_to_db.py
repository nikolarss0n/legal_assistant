#!/usr/bin/env python3
"""
Import labor laws data from JSON into the database.
This script imports previously scraped data into the database.
"""

import os
import sys
from pathlib import Path

from database import HybridDatabaseManager

def import_data():
    """Import data from JSON file into the database"""
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} does not exist.")
        sys.exit(1)
    
    json_file = data_dir / "labor_laws_full.json"
    
    if not json_file.exists():
        print(f"Error: JSON file {json_file} does not exist.")
        sys.exit(1)
    
    # Print message
    print(f"Importing data from {json_file}...")
    
    # Initialize the database manager
    db_manager = HybridDatabaseManager(
        db_path=str(data_dir / "legal_db.sqlite"),
        vector_db_path=str(data_dir / "vector_db")
    )
    
    # Import the data
    db_manager.import_from_json(str(json_file))
    
    print("Import completed successfully!")
    
    # Run a test query to verify the import
    test_query = "трудов договор прекратяване"  # "employment contract termination" in Bulgarian
    print(f"\nRunning test query: '{test_query}'")
    results = db_manager.search_similar(test_query, n_results=3)
    
    print(f"Found {len(results)} relevant results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Similarity: {result['similarity']:.2f}):")
        print(f"Law: {result['metadata']['law_title']}")
        print(f"Article: {result['metadata']['article_number']}")
        print(f"Content snippet: {result['content'][:150]}...")

if __name__ == "__main__":
    import_data()