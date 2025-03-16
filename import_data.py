#!/usr/bin/env python3
"""
Import data from the scraper into the database.
This script serves as a bridge between the scraper and database components.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

from scraper import LexBGScraper
from database import HybridDatabaseManager


async def scrape_and_import():
    """Scrape data and import it into the database"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Placeholder URL - replace with the actual labor law URL from lex.bg
    LABOR_LAW_URL = "https://lex.bg/laws/labor"
    
    print("Starting scraper...")
    async with LexBGScraper(headless=False) as scraper:
        # Navigate to the labor law section
        await scraper.navigate(LABOR_LAW_URL)
        
        # Extract links to individual labor laws
        labor_laws = await scraper.extract_main_law_links()
        
        # Extract content from each law
        all_laws_content = []
        for law in labor_laws:
            print(f"Scraping: {law['title']}")
            law_content = await scraper.extract_law_content(law['url'])
            all_laws_content.append(law_content)
        
        # Save the data to JSON
        json_path = data_dir / "labor_laws.json"
        await scraper.save_to_json(all_laws_content, filename=str(json_path))
    
    print("Scraping completed. Starting database import...")
    
    # Initialize the database manager
    db_manager = HybridDatabaseManager(
        db_path=str(data_dir / "legal_db.sqlite"),
        vector_db_path=str(data_dir / "vector_db")
    )
    
    # Import the data
    db_manager.import_from_json(str(json_path))
    
    print("Import completed successfully!")
    
    # Run a test query to verify the import
    test_query = "worker rights termination"
    print(f"\nRunning test query: '{test_query}'")
    results = db_manager.search_similar(test_query, n_results=3)
    
    print(f"Found {len(results)} relevant results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Similarity: {result['similarity']:.2f}):")
        print(f"Law: {result['metadata']['law_title']}")
        print(f"Article: {result['metadata']['article_number']}")
        print(f"Content snippet: {result['content'][:150]}...")


def main():
    """Main entry point"""
    try:
        asyncio.run(scrape_and_import())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()