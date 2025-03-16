# Bulgarian Legal Assistant

An AI-powered legal assistant that helps Bulgarian citizens understand and navigate legal information from lex.bg.

## Project Overview

This project aims to create an AI-powered legal assistant that:

1. Scrapes legal information from lex.bg
2. Stores it in a hybrid database system (vector + relational)
3. Provides an intelligent interface to query and understand Bulgarian laws

## Components

### Scraper

The scraper module collects legal information from lex.bg, focusing initially on labor law. It:
- Navigates through the website
- Extracts structured data from legal documents
- Saves this information for processing

### Database

A hybrid database system that combines:
- Vector storage for semantic understanding (ChromaDB)
- Relational database for structured metadata (SQLite)

This approach allows for both semantic searches ("what are my rights if I'm fired?") and structured queries ("show me all labor laws from 2020").

### Model Interface

Uses the Gemma 3 foundation model to:
- Process natural language queries
- Search the hybrid database
- Generate helpful, accurate responses about Bulgarian law

The interface can be configured to use either:
- Local installation of Gemma 3
- API access to hosted Gemma 3 model

## Getting Started

### Prerequisites

- Python 3.8+
- Pip for package management

### Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
python -m playwright install
```

### Running the Scraper

```bash
python -m scraper.labor_law_scraper
```

### Setting Up the Database

```bash
python import_to_db.py
```

### Using the Gemma-Powered Legal Assistant

After importing data, you can use the legal assistant to ask questions:

```bash
python legal_query.py
```

Optional arguments:
- `--model`: Specify the Gemma model to use (default: gemma3-9b-it)
- `--api-key`: Provide an API key for Gemma (can also use GEMMA_API_KEY env var)
- `--results`: Number of search results to retrieve (default: 5)
- `--no-sources`: Don't display sources for answers

### Direct Database Querying

For direct database access:

```bash
python query_db.py
```

### Testing the Assistant

Run pre-defined test questions:

```bash
python test_legal_assistant.py
```

## Project Status

This project is in early development. Current focus:
- Implementing the labor law scraper
- Setting up the hybrid database structure
- Planning the model interface architecture

## Legal Disclaimer

This tool is designed to provide general legal information and is not a substitute for professional legal advice. Always consult a qualified lawyer for specific legal issues.

## License

This project is licensed under the MIT License - see the LICENSE file for details.