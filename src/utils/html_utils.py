import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()  # check for HTTP issues
    return BeautifulSoup(response.content, 'html.parser')