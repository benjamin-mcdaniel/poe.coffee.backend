import os
import requests
from bs4 import BeautifulSoup

# Access environment variables
scrape_url = os.getenv('SCRAPE_URL')

if not scrape_url:
    raise ValueError("No URL provided. Please set the SCRAPE_URL environment variable.")

print(f"SCRAPE_URL: {scrape_url}")

# Your BeautifulSoup scraping logic here
response = requests.get(scrape_url)
soup = BeautifulSoup(response.content, 'html.parser')

print(soup.title.text)
