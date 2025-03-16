#!/usr/bin/env python3
"""
Query the legal database interactively.
"""

import os
import sys
from pathlib import Path

from database import HybridDatabaseManager

def main():
    """Query the database interactively"""
    data_dir = Path("data")
    
    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} does not exist.")
        sys.exit(1)
    
    db_path = data_dir / "legal_db.sqlite"
    vector_db_path = data_dir / "vector_db"
    
    if not db_path.exists():
        print(f"Error: Database file {db_path} does not exist.")
        print("Please run import_to_db.py first to import the data.")
        sys.exit(1)
    
    print(f"Connecting to database at {db_path}...")
    
    # Initialize the database manager
    db_manager = HybridDatabaseManager(
        db_path=str(db_path),
        vector_db_path=str(vector_db_path)
    )
    
    print("Database connected successfully!")
    
    # Display some help information
    print("\nWelcome to the Legal Database Query Tool!")
    print("------------------------------------------")
    print("You can search the Bulgarian Labor Code for specific topics.")
    print("Example queries:")
    print("  - трудов договор")
    print("  - отпуск")
    print("  - прекратяване на трудови отношения")
    print("\nType 'exit' or 'quit' to exit the program.")
    
    while True:
        # Get query from user
        query = input("\nEnter your query: ")
        
        # Check if the user wants to exit
        if query.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        # Perform the search
        n_results = 5  # Number of results to return
        try:
            print(f"Searching for: '{query}'")
            results = db_manager.search_similar(query, n_results=n_results)
            
            print(f"\nFound {len(results)} relevant results:")
            for i, result in enumerate(results):
                print(f"\nResult {i+1} (Similarity: {result['similarity']:.2f}):")
                print(f"Law: {result['metadata']['law_title']}")
                print(f"Article: {result['metadata']['article_number']}")
                
                # Display a snippet of the content (first 150 characters)
                content_snippet = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
                print(f"Content snippet: {content_snippet}")
                
                # Ask if the user wants to see the full content
                if i < len(results) - 1:  # Don't ask for the last result
                    see_full = input("\nSee full content? (y/n/next/all): ").lower()
                    if see_full == "y":
                        print("\nFull content:")
                        print("-" * 50)
                        print(result['content'])
                        print("-" * 50)
                    elif see_full == "all":
                        print("\nFull content:")
                        print("-" * 50)
                        print(result['content'])
                        print("-" * 50)
                        # Show all remaining results without asking
                        for j, res in enumerate(results[i+1:]):
                            print(f"\nResult {i+j+2} (Similarity: {res['similarity']:.2f}):")
                            print(f"Law: {res['metadata']['law_title']}")
                            print(f"Article: {res['metadata']['article_number']}")
                            print("\nFull content:")
                            print("-" * 50)
                            print(res['content'])
                            print("-" * 50)
                        break  # Break the loop to start a new query
                    elif see_full == "next":
                        continue  # Skip to the next result
                else:
                    # For the last result, always ask
                    see_full = input("\nSee full content? (y/n): ").lower()
                    if see_full == "y":
                        print("\nFull content:")
                        print("-" * 50)
                        print(result['content'])
                        print("-" * 50)
        except Exception as e:
            print(f"Error performing search: {e}")

if __name__ == "__main__":
    main()