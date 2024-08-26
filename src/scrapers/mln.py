import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from schemas.schemas import Content
from utils.html_utils import fetch_html, get_cms_webpage_content
from utils.pdf_utils import extract_text_from_pdf_url
from utils.text_utils import clean_and_split_paragraphs
import requests
from scrapers.scraper import DataSource

from utils.log_config import setup_logger

logger = setup_logger(__name__)

class MLNNewsletter(DataSource):
    def __init__(self):
        super().__init__()
        
        self.source_name = 'MLN Newsletter'
        
        self.base_url = 'https://www.cms.gov'
        self.newsletter_url = f'{self.base_url}/training-education/medicare-learning-network/newsletter'

    def fetch(self, n_days=7):
        newsletters = []
        
        for day_offset in range(n_days):
            # calculate date for current loop iteration
            date_to_fetch = datetime.now() - timedelta(days=day_offset)
            newsletter_url = f'{self.newsletter_url}/{date_to_fetch.strftime("%Y-%m-%d")}-mlnc'
            
            try:
                # fetch html for current date
                soup = fetch_html(newsletter_url)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    continue  # skip to next date if 404 error occurs (no newsletter on this day)
                else:
                    logger.error(f"HTTP error for {newsletter_url}: {str(e)}")
                    newsletters.append(self.manual_check_required(newsletter_url))
                    continue
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {newsletter_url}: {str(e)}")
                newsletters.append(self.manual_check_required(newsletter_url))
                continue
            except Exception as e:
                logger.error(f"Unexpected error while fetching {newsletter_url}: {str(e)}")
                newsletters.append(self.manual_check_required(newsletter_url))
                continue

            article = soup.find('article')
            if not article:
                # skip this iteration if article not found
                logger.error(f"Article not found in {newsletter_url}")
                newsletters.append(self.manual_check_required(newsletter_url))
                continue

            # parse toc section to create mapping of toc ids to respective titles
            toc_mapping = {}
            toc_links = article.select('a[href^="#_Toc"]')

            for link in toc_links:
                toc_id = link.get('href').replace('#', '')
                heading_text = link.get_text(strip=True)
                toc_mapping[toc_id] = heading_text

            # parse main content and map to toc
            sections = article.find_all(['h2', 'h3'])

            for section in sections:
                toc_ids = [anchor.get('id') for anchor in section.find_all('a', id=True) if anchor.get('id').startswith("_Toc")]

                if toc_ids:
                    for toc_id in toc_ids:
                        heading_text = toc_mapping.get(toc_id, None)
                        if heading_text is None:
                            continue  # skip if heading text not found

                        content_text = []
                        links = []

                        # traverse sibling elements to find associated text and links
                        next_sibling = section.find_next_sibling()
                        while next_sibling and next_sibling.name not in ['h2', 'h3']:
                            content_text.append(next_sibling.get_text())

                            # extract links
                            for link in next_sibling.find_all('a'):
                                link_href = link.get('href')
                                link_text = link.text
                                
                                if link_href is None:
                                    continue
                                
                                # if it's an internal file
                                if link_href.startswith('/'):
                                    link_href = self.base_url + link_href
                                    
                                links.append(link_href)
                                
                                try:
                                    if link_href.endswith('.pdf'):
                                        text = extract_text_from_pdf_url(link_href)
                                    elif link_href.endswith('.txt'):
                                        text = requests.get(link_href).text
                                    elif link_href.startswith(self.base_url):
                                        text =  get_cms_webpage_content(link_href)
                                    elif link_href.startswith('http'):
                                        text = fetch_html(link_href).text
                                    elif link_href.startswith('mailto:'):
                                        continue  # this is an email link, skip
                                    else:
                                        logger.error(f"Unsupported link type: {link_href}")
                                        newsletters.append(self.manual_check_required(link_href))
                                        continue
                                except Exception as e:
                                    logger.error(f"Error while fetching link {link_href}: {str(e)}")
                                    newsletters.append(self.manual_check_required(link_href))
                                    continue
                                    
                                text = clean_and_split_paragraphs(text)
                                metadata = {
                                    'Newsletter Heading': heading_text,
                                    'Link Text': link_text,
                                    'Newsletter URL':  f"{newsletter_url}#{toc_id}",
                                }
                                newsletter = Content(
                                    source='MLN Newsletter, Additional Link',
                                    sections=text,
                                    url=link_href,
                                    metadata=metadata
                                )
                                newsletters.append(newsletter)

                            next_sibling = next_sibling.find_next_sibling()

                        full_text = " ".join(content_text).strip()
                        if not full_text:
                            continue  # skip if no content found
                        
                        full_text = clean_and_split_paragraphs(full_text)

                        metadata = {
                            'Heading': heading_text,
                            'TOC ID': toc_id,
                            'Links': ', '.join(links),
                        }

                        newsletter = Content(
                            source=self.source_name,
                            sections=full_text,
                            url=f"{newsletter_url}#{toc_id}",
                            metadata=metadata
                        )

                        newsletters.append(newsletter)

        return newsletters
