#!/usr/bin/env python3
"""
Test script for the legal assistant with pre-defined questions.
"""

import sys
from pathlib import Path

from database import HybridDatabaseManager
from model.gemma_interface import LegalAssistant

def test_legal_assistant():
    """Test the legal assistant with some sample questions"""
    # Setup paths
    data_dir = Path("data")
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
    
    # Initialize the legal assistant
    legal_assistant = LegalAssistant(
        db_manager=db_manager,
        model_name="gemma3-9b-it"
    )
    
    # Test questions
    test_questions = [
        "How many days of annual leave am I entitled to?",
        "What are the requirements for terminating a labor contract?",
        "What is the minimum wage in Bulgaria?",
        "Can my employer change my job position without my consent?",
        "What happens if my employer doesn't pay my salary on time?",
    ]
    
    print("\nRunning tests with sample questions...\n")
    
    # Process each question
    for i, question in enumerate(test_questions):
        print(f"Question {i+1}: {question}")
        
        # Get answer from the legal assistant
        result = legal_assistant.answer_question(
            question=question,
            max_results=3
        )
        
        # Display the answer
        print("\nAnswer:")
        print(result["answer"])
        
        # Display sources
        print("\nSources:")
        for j, source in enumerate(result["sources"]):
            print(f"[{j+1}] {source['title']} - {source['article']} (Relevance: {source['relevance']})")
        
        print("\n" + "-" * 80)

if __name__ == "__main__":
    test_legal_assistant()