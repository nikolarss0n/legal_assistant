#!/usr/bin/env python3
"""
Script to check HTML structure of the labor law page.
"""

import asyncio
from playwright.async_api import async_playwright

# Base URL for the Bulgarian legal website
BASE_URL = "https://lex.bg"
# Labor Code (Кодекс на труда) direct URL
LABOR_LAW_URL = f"{BASE_URL}/laws/ldoc/1594373121"

async def check_html_structure():
    """Check the HTML structure of the labor law page to understand the structure."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"Navigating to {LABOR_LAW_URL}")
        await page.goto(LABOR_LAW_URL, wait_until="networkidle")
        
        # Check if the ".boxi boxinb" locator exists
        boxi_elements = await page.query_selector_all(".boxi.boxinb")
        if not boxi_elements:
            print("No elements found with class '.boxi.boxinb'")
            # Try with separate classes
            boxi_elements = await page.query_selector_all(".boxi")
            if boxi_elements:
                print(f"Found {len(boxi_elements)} elements with class '.boxi'")
                
            boxinb_elements = await page.query_selector_all(".boxinb")
            if boxinb_elements:
                print(f"Found {len(boxinb_elements)} elements with class '.boxinb'")
        else:
            print(f"Found {len(boxi_elements)} elements with class '.boxi.boxinb'")
            
            # Check the content of the first element
            if boxi_elements:
                first_element = boxi_elements[0]
                content = await first_element.inner_text()
                print(f"\nSample content from first element (first 200 chars):\n{content[:200]}...")
                
                # Check for structural elements inside
                sections = await first_element.query_selector_all("div, section, article")
                print(f"\nFound {len(sections)} div/section/article elements inside")
                
                # Check if there are any article headers or markers
                article_markers = await first_element.query_selector_all("h1, h2, h3, h4, h5")
                print(f"Found {len(article_markers)} header elements inside")
                
                # Check for paragraphs which might be individual articles
                paragraphs = await first_element.query_selector_all("p")
                print(f"Found {len(paragraphs)} paragraph elements inside")
                
                # Extract HTML to analyze structure
                html = await first_element.inner_html()
                print(f"\nHTML structure sample (first 500 chars):\n{html[:500]}...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_html_structure())