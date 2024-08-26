import re
from datetime import datetime, timedelta

from utils.pdf_utils import extract_text_from_pdf_url
from schemas.schemas import Content
from utils.html_utils import fetch_html

from scrapers.scraper import DataSource

from utils.log_config import setup_logger

logger = setup_logger(__name__)

class CMS(DataSource):
    def __init__(self):
        super().__init__()
        
        self.source_name = 'CMS Transmittals'
        
        self.base_url = 'https://www.cms.gov'
        self.transmittals_url = self.base_url + f'/medicare/regulations-guidance/transmittals/{datetime.now().year}-transmittals'
    
    def fetch(self, n_days=7):
        # parse main transmittals page
        try:
            soup = fetch_html(self.transmittals_url)
        except Exception as e:
            logger.error(f"Failed to fetch transmittals page: {e}")
            return [self.manual_check_required(self.transmittals_url)]

        # extract the table and rows
        try:
            transmittal_table = soup.find('table')
            rows = transmittal_table.find_all('tr')
        except Exception as e:
            logger.error(f"Failed to find or parse transmittal table: {e}")
            return [self.manual_check_required(self.transmittals_url)]

        # get date range for the last n days
        today = datetime.now()
        seven_days_ago = today - timedelta(days=n_days)

        # get transmittals
        recent_transmittals = []
        for row in rows[1:]:  # skip the header
            try:
                cells = row.find_all('td')
                if len(cells) > 1:
                    date_text = cells[1].get_text(strip=True)
                    transmittal_date = datetime.strptime(date_text, '%Y-%m-%d')
                
                    if seven_days_ago <= transmittal_date <= today:
                        transmittal_link_tag = cells[0].find('a')
                        if transmittal_link_tag:
                            transmittal_link = transmittal_link_tag['href']
                            transmittal_url = self.base_url + transmittal_link
                            try:
                                transmittal_page = fetch_html(transmittal_url)
                            except Exception as e:
                                logger.error(f"Failed to fetch transmittal page: {transmittal_url}, error: {e}")
                                recent_transmittals.append(self.manual_check_required(transmittal_url))
                                continue
                        
                            # extract link to the actual document
                            downloads_section = transmittal_page.find('div', class_='field--name-field-downloads')
                            if downloads_section:
                                document_link_tag = downloads_section.find('a')
                                if document_link_tag:
                                    document_link = document_link_tag['href']
                                    document_url = self.base_url + document_link
                                    
                                    try:
                                        content = extract_text_from_pdf_url(document_url)
                                    except Exception as e:
                                        logger.error(f"Cannot download or extract text from: {document_url}, error: {e}")
                                        recent_transmittals.append(self.manual_check_required(document_url))
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
                                    
                                    transmittal = Content(
                                        source='CMS Transmittals',
                                        sections=paragraphs,
                                        url=document_url,
                                        metadata=transmittal_info
                                    )
                                    recent_transmittals.append(transmittal)
                            else:
                                recent_transmittals.append(self.manual_check_required(transmittal_url))
            except Exception as e:
                continue

        return recent_transmittals
