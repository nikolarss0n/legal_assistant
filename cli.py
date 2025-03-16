#!/usr/bin/env python3
"""
Command-line interface for the legal assistant.
This allows users to interact with the legal assistant via the command line.
"""

import os
import sys
import argparse
from pathlib import Path

from database import HybridDatabaseManager
from model import LegalAssistant


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Bulgarian Legal Assistant CLI')
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='data/legal_db.sqlite',
        help='Path to the SQLite database file'
    )
    
    parser.add_argument(
        '--vector-db-path',
        type=str,
        default='data/vector_db',
        help='Path to the vector database directory'
    )
    
    parser.add_argument(
        '--model-path',
        type=str,
        help='Path to the local model (optional)'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='API key for model access (optional)'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        help='Filter results by category (e.g., "labor")'
    )
    
    return parser.parse_args()


def main():
    """Main CLI function"""
    args = parse_args()
    
    # Check if database exists
    if not os.path.exists(args.db_path):
        print(f"Error: Database file not found at {args.db_path}")
        print("Please run import_data.py first to create the database.")
        sys.exit(1)
    
    # Initialize database manager
    db_manager = HybridDatabaseManager(
        db_path=args.db_path,
        vector_db_path=args.vector_db_path
    )
    
    # Initialize legal assistant
    assistant = LegalAssistant(
        db_manager=db_manager,
        model_path=args.model_path,
        api_key=args.api_key
    )
    
    print("=" * 80)
    print("Bulgarian Legal Assistant")
    print("=" * 80)
    print("Ask questions about Bulgarian law, or type 'exit' to quit.")
    print("=" * 80)
    
    while True:
        try:
            # Get user input
            question = input("\nQuestion: ").strip()
            
            # Exit condition
            if question.lower() in ('exit', 'quit', 'q'):
                break
            
            # Skip empty questions
            if not question:
                continue
            
            # Prepare filters
            filters = {}
            if args.category:
                filters['category'] = args.category
            
            # Get answer
            result = assistant.answer_question(
                question=question,
                filters=filters
            )
            
            # Print answer
            print("\n" + "=" * 80)
            print("Answer:")
            print(result['answer'])
            
            # Print sources
            if result['sources']:
                print("\nSources:")
                for i, source in enumerate(result['sources']):
                    print(f"  {i+1}. {source['title']} - {source['article']} (Relevance: {source['relevance']})")
            
            print("=" * 80)
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()