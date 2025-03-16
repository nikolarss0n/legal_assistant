#!/usr/bin/env python3
"""
Labor Law Scraper for lex.bg
This script scrapes labor law information from lex.bg and saves it to a structured format.
"""

import os
import json
import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import pandas as pd
from playwright.async_api import async_playwright, Page, Browser

# Base URL for the Bulgarian legal website
BASE_URL = "https://lex.bg"
# Labor Code (Кодекс на труда) direct URL
LABOR_LAW_URL = f"{BASE_URL}/laws/ldoc/1594373121"


class LexBGScraper:
    """Scraper class for extracting labor law data from lex.bg"""

    def __init__(self, headless: bool = True):
        """
        Initialize the scraper

        Args:
            headless: Whether to run the browser in headless mode
        """
        self.headless = headless
        self.browser = None
        self.page = None
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)

    async def __aenter__(self):
        """Context manager entry point"""
        playwright = await async_playwright().__aenter__()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point"""
        if self.browser:
            await self.browser.close()

    async def navigate(self, url: str):
        """Navigate to a URL"""
        await self.page.goto(url, wait_until="networkidle")
        print(f"Navigated to {url}")

    async def extract_main_law_links(self) -> List[Dict[str, str]]:
        """
        For the Labor Code, we'll use a different approach since we're directly
        accessing the Labor Code page rather than a list of laws.

        Returns:
            List containing the Labor Code as a dictionary
        """
        laws = []
        try:
            # Wait for the content to load
            await self.page.wait_for_selector("h1", timeout=10000)

            # Get the title
            title = await self.page.inner_text("h1")

            # Add the Labor Code to our list
            laws.append({"title": title.strip(), "url": LABOR_LAW_URL})

            print(f"Using Labor Code: {title.strip()}")

            # For testing purposes, we can add additional sections/chapters
            # by finding links to specific articles
            try:
                article_links = await self.page.query_selector_all(".toc a")

                if article_links and len(article_links) > 0:
                    for link_el in article_links[:5]:  # Limit to first 5 for testing
                        article_text = await link_el.inner_text()
                        article_href = await link_el.get_attribute("href")

                        if article_href:
                            laws.append(
                                {
                                    "title": f"{title.strip()} - {article_text.strip()}",
                                    "url": (
                                        f"{BASE_URL}{article_href}"
                                        if not article_href.startswith("http")
                                        else article_href
                                    ),
                                }
                            )
            except Exception as e:
                print(f"Note: Could not extract additional article links: {e}")

            print(f"Found {len(laws)} law items to scrape")

        except Exception as e:
            print(f"Error extracting main labor code: {e}")
            # Fallback to just use the URL we already have
            laws.append({"title": "Кодекс на труда (Labor Code)", "url": LABOR_LAW_URL})

        return laws

    async def extract_law_content(self, law_url: str) -> Dict[str, Any]:
        """
        Extract content from a specific law page

        Args:
            law_url: URL of the law page

        Returns:
            Dictionary containing structured law content
        """
        await self.navigate(law_url)

        try:
            # Wait for the content to load
            await self.page.wait_for_selector("h1, #DocumentTitle .Title", timeout=10000)

            # Get the title
            title_element = await self.page.query_selector("h1, #DocumentTitle .Title")
            title = await title_element.inner_text() if title_element else "Labor Code"

            # Try to get date information
            date_published = ""
            try:
                # Look for text that might contain publication date info
                date_text = await self.page.inner_text(".TitleDocument")
                if date_text:
                    # Extract date information using common patterns in Bulgarian legal documents
                    if "Обн. ДВ" in date_text:
                        date_published = date_text.split("Обн. ДВ")[1].split(",")[0].strip()
                    else:
                        date_published = date_text
            except Exception:
                date_published = "Date information not available"

            # Extract articles - now using the new ".boxi.boxinb" selector
            articles = []
            
            # Check if the ".boxi.boxinb" element exists
            codex_container = await self.page.query_selector(".boxi.boxinb")
            
            if codex_container:
                print("Found main codex container with class '.boxi.boxinb'")
                
                # Get the full text of the codex
                full_text = await codex_container.inner_text()
                
                # Extract articles based on the "Чл." marker
                # This is a simple implementation - we can refine it if needed
                segments = []
                current_segment = ""
                
                # Split the text into lines
                lines = full_text.split("\n")
                article_num = "Preamble"
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this line starts a new article
                    if line.startswith("Чл.") or (line.startswith("Член") and len(line) < 30):
                        # Save the previous segment if it exists
                        if current_segment:
                            segments.append({
                                "number": article_num,
                                "content": current_segment.strip()
                            })
                        
                        # Extract the article number using regex
                        match = re.match(r'Чл\.\s*(\d+[а-я]*)\.?', line)
                        if match:
                            article_num = f"Чл. {match.group(1)}"
                        else:
                            # Fallback to just using the first word
                            words = line.split()
                            if words and words[0].startswith("Чл"):
                                article_num = words[0]
                            else:
                                article_num = "Чл."
                        
                        current_segment = line
                    else:
                        # Continue the current segment
                        current_segment += "\n" + line
                
                # Don't forget to add the last segment
                if current_segment:
                    segments.append({
                        "number": article_num,
                        "content": current_segment.strip()
                    })
                
                # Clean up and finalize the segments
                for segment in segments:
                    # Skip empty segments and navigation elements
                    if (len(segment["content"]) > 10 and 
                        "ДОБАВИ В МОИТЕ АКТОВЕ" not in segment["content"] and
                        "LEX.BG" not in segment["content"]):
                        articles.append(segment)
                
                print(f"Extracted {len(articles)} article segments from the codex")
            else:
                # Fallback to the previous strategies if we don't find the new container
                print("Codex container not found with class '.boxi.boxinb', trying fallback methods")
                
                # Strategy 1: Check for article elements with class
                article_elements = await self.page.query_selector_all(".article")

                if not article_elements or len(article_elements) == 0:
                    # Strategy 2: Try to find elements with article IDs
                    article_elements = await self.page.query_selector_all("[id^='art']")

                if not article_elements or len(article_elements) == 0:
                    # Strategy 3: Look for paragraphs within the content section
                    main_content = await self.page.query_selector(
                        ".content, main, .law-content"
                    )
                    if main_content:
                        article_elements = await main_content.query_selector_all("p")

                # Process article elements if we found any
                for article_el in article_elements:
                    try:
                        # Try to find article number and content
                        article_id = await article_el.get_attribute("id")
                        article_num = article_id if article_id else "Unknown"

                        # Get the text content
                        content = await article_el.inner_text()

                        # If content contains the article number at the beginning, extract it
                        if content.startswith("Чл.") or content.startswith("Art."):
                            parts = content.split(".", 1)
                            if len(parts) > 1:
                                article_num = f"Чл. {parts[0].replace('Чл', '').strip()}"
                                content = parts[1].strip()

                        articles.append(
                            {"number": article_num.strip(), "content": content.strip()}
                        )
                    except Exception as e:
                        print(f"Error extracting article: {e}")

            # Take a screenshot of the law page for reference
            screenshot_path = (
                self.data_dir / f"screenshot_{title.replace(' ', '_')}.png"
            )
            await self.page.screenshot(path=str(screenshot_path))

            return {
                "title": title.strip(),
                "url": law_url,
                "date_published": date_published.strip(),
                "scraped_date": datetime.now().isoformat(),
                "articles": articles,
            }

        except Exception as e:
            print(f"Error extracting law content from {law_url}: {e}")
            return {
                "url": law_url,
                "error": str(e),
                "scraped_date": datetime.now().isoformat(),
            }

    async def save_to_json(
        self, data: List[Dict[str, Any]], filename: str = "labor_laws.json"
    ):
        """Save the scraped data to a JSON file"""
        filepath = self.data_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {filepath}")

    async def save_to_csv(
        self, data: List[Dict[str, Any]], filename: str = "labor_laws.csv"
    ):
        """Save the scraped data to a CSV file (flattened structure)"""
        # Flatten the nested structure for CSV format
        flattened_data = []

        for law in data:
            if "error" in law:
                # Skip laws that had errors during scraping
                continue

            base_info = {
                "title": law.get("title", ""),
                "url": law.get("url", ""),
                "date_published": law.get("date_published", ""),
                "scraped_date": law.get("scraped_date", ""),
            }

            # Add each article as a separate row
            for article in law.get("articles", []):
                article_info = base_info.copy()
                article_info["article_number"] = article.get("number", "")
                article_info["article_content"] = article.get("content", "")
                flattened_data.append(article_info)

        # Convert to DataFrame and save
        df = pd.DataFrame(flattened_data)
        filepath = self.data_dir / filename
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"Data saved to {filepath}")


async def main():
    """Main entry point for the scraper"""
    # Create data directory if it doesn't exist
    Path("./data").mkdir(exist_ok=True)

    # Set headless to False to see the browser (useful for debugging)
    async with LexBGScraper(headless=False) as scraper:
        print(f"Starting scraper for Labor Code at {LABOR_LAW_URL}")

        # Navigate to the labor code page
        await scraper.navigate(LABOR_LAW_URL)

        # Now we'll just extract the full labor code directly from the main URL
        # rather than extracting links to individual articles
        print("Extracting the full Labor Code from the main page...")
        labor_law_content = await scraper.extract_law_content(LABOR_LAW_URL)
        
        # Print some stats for the scraped content
        article_count = len(labor_law_content.get("articles", []))
        print(f"Found {article_count} articles/content blocks in the Labor Code")
        
        # Save the data
        all_laws_content = [labor_law_content]
        await scraper.save_to_json(all_laws_content, filename="labor_laws_full.json")
        await scraper.save_to_csv(all_laws_content, filename="labor_laws_full.csv")
        
        print("\nScraping completed. Saved to 'labor_laws_full.json' and 'labor_laws_full.csv'")
        
        # Optionally, you can still use the old approach to extract individual article links
        # if you need more granularity
        if False:  # Change to True if you want to use the links approach
            # Extract links to chapters or articles
            labor_laws = await scraper.extract_main_law_links()
            
            # Extract content from each law/article
            additional_content = []
            
            for i, law in enumerate(labor_laws):
                if law["url"] != LABOR_LAW_URL:  # Skip the main URL we already scraped
                    print(f"Scraping additional link {i+1}/{len(labor_laws)}: {law['title']}")
                    law_content = await scraper.extract_law_content(law["url"])
                    additional_content.append(law_content)
                    
                    # Pause briefly between requests
                    if i < len(labor_laws) - 1:
                        await asyncio.sleep(1)
            
            # Save additional content if any was found
            if additional_content:
                await scraper.save_to_json(additional_content, filename="labor_laws_additional.json")
                await scraper.save_to_csv(additional_content, filename="labor_laws_additional.csv")
                print("Additional content saved to 'labor_laws_additional.json' and 'labor_laws_additional.csv'")


if __name__ == "__main__":
    asyncio.run(main())
