import re
from datetime import datetime, timedelta

from utils.pdf_utils import extract_text_from_pdf_url
from schemas.schemas import TextSchema
from utils.html_utils import fetch_html

class CMS:
    def __init__(self):
        self.base_url = 'https://www.cms.gov'
        self.transmittals_url = self.base_url + f'/medicare/regulations-guidance/transmittals/{datetime.now().year}-transmittals'
    
    def fetch(self, n_days=7):
        # parse main transmittals page
        soup = fetch_html(self.transmittals_url)

        # extract the table and rows
        transmittal_table = soup.find('table')
        rows = transmittal_table.find_all('tr')

        # get date range for the last n days
        today = datetime.now()
        seven_days_ago = today - timedelta(days=n_days)

        # get transmittals
        recent_transmittals = []
        for row in rows[1:]:  # skip the header
            cells = row.find_all('td')
            if len(cells) > 1:
                date_text = cells[1].get_text(strip=True)
                transmittal_date = datetime.strptime(date_text, '%Y-%m-%d')
                
                if seven_days_ago <= transmittal_date <= today:
                    transmittal_link_tag = cells[0].find('a')
                    if transmittal_link_tag:
                        transmittal_link = transmittal_link_tag['href']
                        transmittal_url = self.base_url + transmittal_link
                        transmittal_page = fetch_html(transmittal_url)
                        
                        # extract link to the actual document
                        downloads_section = transmittal_page.find('div', class_='field--name-field-downloads')
                        if downloads_section:
                            document_link_tag = downloads_section.find('a')
                            if document_link_tag:
                                document_link = document_link_tag['href']
                                document_url = self.base_url + document_link
                                
                                try:
                                    content = extract_text_from_pdf_url(document_url)
                                except Exception:
                                    print(f"Cannot download: {document_url}")
                                    continue
                                
                                transmittal_info = {
                                    'Transmittal #': transmittal_link_tag.get_text(strip=True),
                                    'Issue Date': date_text,
                                    'Subject': cells[2].get_text(strip=True),
                                    'Implementation Date': cells[3].get_text(strip=True),
                                    'CR #': cells[4].get_text(strip=True),
                                }
                                
                                sections = re.split(r'SUBJECT:', content)
                                sections = [para for section in sections for para in re.split(r"\n\s*\n+", section)]
                                pattern = re.compile(r'.*[.!?]$', re.MULTILINE)
                                paragraphs = [section for section in sections if pattern.search(section.strip())]
                                
                                transmittal = TextSchema(
                                    sections=paragraphs,
                                    url=document_url,
                                    metadata=transmittal_info
                                )
                                recent_transmittals.append(transmittal)
        return recent_transmittals
    
    