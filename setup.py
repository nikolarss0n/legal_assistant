#!/usr/bin/env python3
"""
Setup script for the legal assistant project.
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install project dependencies"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("Installing Playwright browsers...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install"])

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = [
        "data",
        "data/vector_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def welcome_message():
    """Print a welcome message with instructions"""
    print("\n" + "=" * 80)
    print("Bulgarian Legal Assistant Setup")
    print("=" * 80)
    print("\nSetup completed successfully!")
    print("\nTo run the scraper and import data:")
    print("  python import_data.py")
    print("\nNext steps:")
    print("1. Update the LABOR_LAW_URL in import_data.py with the correct URL from lex.bg")
    print("2. Adjust the scraper selectors in labor_law_scraper.py to match the actual HTML structure")
    print("3. Run the import script to collect and process the data")
    print("\nHappy coding!")
    print("=" * 80 + "\n")

def main():
    """Main setup function"""
    try:
        install_dependencies()
        create_directories()
        welcome_message()
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()