#!/usr/bin/env python3
"""
Advanced legal query tool using Gemma model.
This script connects the database with the Gemma model to provide more intelligent
legal answers based on the Bulgarian labor code.
"""

import os
import sys
from pathlib import Path
import argparse
from typing import Optional, Dict, Any

from database import HybridDatabaseManager
from model.gemma_interface import LegalAssistant

def main(args):
    """Main entry point for the legal query tool"""
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
    
    # Initialize the legal assistant with advanced options
    legal_assistant = LegalAssistant(
        db_manager=db_manager,
        model_name=args.model,
        model_path=args.model_path,
        api_key=args.api_key,
        config={
            "quantize": args.quantize,
            "device": args.device,
            "temperature": args.temperature
        }
    )
    
    print("\nWelcome to the LexBG Assistant!")
    print("-------------------------------")
    print("Ask questions about Bulgarian labor law in natural language.")
    print("The assistant will search the law database and provide answers.")
    print("\nExample questions:")
    print("  - How many days of annual leave am I entitled to?")
    print("  - What are the requirements for terminating a labor contract?")
    print("  - Can my employer change my job position without my consent?")
    print("\nType 'exit' or 'quit' to exit the program.")
    
    while True:
        # Get query from user
        question = input("\nYour question: ")
        
        # Check if the user wants to exit
        if question.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        # Get answer from the legal assistant
        result = legal_assistant.answer_question(
            question=question,
            max_results=args.results
        )
        
        # Display the answer
        print("\n=== Answer ===")
        print(result["answer"])
        
        # Display sources if available and requested
        if result["sources"] and not args.no_sources:
            print("\n=== Sources ===")
            for i, source in enumerate(result["sources"]):
                print(f"[{i+1}] {source['title']} - {source['article']} (Relevance: {source['relevance']})")
        
        print("\n" + "-" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Legal Assistant powered by Gemma")
    # Model selection arguments
    model_group = parser.add_argument_group("Model Selection")
    model_group.add_argument("--model", type=str, default="gemma3-9b-it", 
                        help="Model name/ID to use from Hugging Face (e.g., google/gemma-3-8b-it)")
    model_group.add_argument("--model-path", type=str, default=None,
                        help="Path to local model directory (takes precedence over --model)")
    model_group.add_argument("--api-key", type=str, default=None,
                        help="API key for Gemma access (can also be set via GEMMA_API_KEY or HUGGINGFACE_TOKEN env var)")
    
    # Model configuration
    config_group = parser.add_argument_group("Model Configuration")
    config_group.add_argument("--quantize", type=str, choices=["4bit", "8bit", "none"], default="none",
                        help="Quantization level for the model to reduce memory usage")
    config_group.add_argument("--device", type=str, choices=["auto", "cpu", "cuda"], default="auto",
                        help="Device to run the model on (auto selects GPU if available)")
    
    # Assistant behavior
    assistant_group = parser.add_argument_group("Assistant Behavior")
    assistant_group.add_argument("--results", type=int, default=5,
                        help="Maximum number of search results to retrieve")
    assistant_group.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature for text generation (higher = more creative)")
    assistant_group.add_argument("--no-sources", action="store_true",
                        help="Don't display sources for answers")
    
    args = parser.parse_args()
    
    # Update model name if using model path
    if args.model_path:
        print(f"Using local model at {args.model_path}")
    else:
        print(f"Using Hugging Face model: {args.model}")
    
    # Check for API key in environment if not provided
    if not args.api_key:
        api_key = os.environ.get("GEMMA_API_KEY") or os.environ.get("HUGGINGFACE_TOKEN")
        if api_key:
            args.api_key = api_key
            print("Using API key from environment variables")
    
    main(args)