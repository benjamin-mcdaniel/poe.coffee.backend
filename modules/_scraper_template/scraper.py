import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the URL from the environment variable
url = os.getenv('SCRAPE_URL')

if not url:
    raise ValueError("No URL provided. Please set the SCRAPE_URL environment variable.")

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code != 200:
    raise Exception(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Parse the content of the response with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find and print all the <h1> tags
for h1_tag in soup.find_all('h1'):
    print(h1_tag.text)
