import re

def clean_and_split_paragraphs(text):
    cleaned_text = re.sub(r"[^\w\s.,;:!?()$%\[\]-]+", "", text)
    cleaned_text = re.sub(r"(\n\s*\n)+", "\n", cleaned_text)
    paragraphs = [para.strip() for para in cleaned_text.split('\n') if para.strip()]
    return paragraphs