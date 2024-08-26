import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()  # check for HTTP issues
    return BeautifulSoup(response.content, 'html.parser')

def get_cms_webpage_content(url):
    response = requests.get(url)
    response.raise_for_status()  # check for HTTP issues
    soup = BeautifulSoup(response.content, "html.parser")

    main_content = soup.find("div", class_="node__content")

    paragraphs = main_content.find_all("p")
    return '\n\n'.join([para.get_text() for para in paragraphs])