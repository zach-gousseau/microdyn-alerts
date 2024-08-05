import requests
import fitz  # PyMuPDF

def extract_text_from_pdf_url(pdf_url, max_pages=100):
    print(f'Downloading {pdf_url}')
    response = requests.get(pdf_url)
    pdf_content = response.content
    text = ""
    with fitz.open(stream=pdf_content, filetype="pdf") as pdf:
        for i in range(min(len(pdf), max_pages)):
            page = pdf.load_page(i)
            text += page.get_text("text") + "\n"
    return text