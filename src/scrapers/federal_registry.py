import re
import chardet
import email
from email.header import decode_header
import requests
from datetime import datetime, timedelta

from schemas.schemas import Content
from utils.email_utils import EmailClient

from scrapers.scraper import DataSource

from utils.log_config import setup_logger

logger = setup_logger(__name__)

class FederalRegistry(DataSource):
    def __init__(self):
        super().__init__()
        
        self.source_name = 'CMS Federal Registry'
        
        self.email_client = EmailClient()
        self.federal_registry_email = "fedreg@listserv1.access.gpo.gov"

        self.agencies_of_interest = [
            "Centers for Medicare & Medicaid Services",
            "Health and Human Services Department",
            "National Institutes of Health",
            "Indian Health Services"
        ]
        
    def fetch(self, n_days=7):

        # search for recent emails 
        date_range = (datetime.now() - timedelta(days=n_days)).strftime('%d-%b-%Y')
        try:
            status, messages = self.email_client.mail.search(None, f'SINCE {date_range}')
            if status != 'OK':
                raise RuntimeError('Error searching emails')

            email_ids = messages[0].split()

            if not email_ids:
                logger.info('No emails found in the given date range')
                return []

        except Exception as e:
            logger.error(f'Error during email search: {str(e)}')
            return []

        transmittals = []
        for email_id in email_ids:
            try:
                # fetch email by id
                status, msg_data = self.email_client.mail.fetch(email_id, "(RFC822)")
                if status != 'OK':
                    raise RuntimeError(f'Error fetching email id {email_id}')

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        email_from = msg.get("From", "")
                        email_subject = msg.get("Subject", "")
                        email_date = msg.get("Date", "")

                        if self.federal_registry_email in email_from:
                            
                            # decode email subject if encoded
                            decoded_subject, encoding = decode_header(email_subject)[0]
                            if isinstance(decoded_subject, bytes):
                                decoded_subject = decoded_subject.decode(encoding if encoding else "utf-8")
                            logger.info(f"New email from {email_from}: {decoded_subject}")

                            # fetch email body
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))

                                    # decode email part payload
                                    raw_payload = part.get_payload(decode=True)

                                    if raw_payload:
                                        detected_encoding = chardet.detect(raw_payload).get('encoding', 'utf-8')

                                        if content_type == "text/plain" and "attachment" not in content_disposition:
                                            email_body = raw_payload.decode(detected_encoding)
                                            agency_updates = self.get_links_from_text_email(email_body)
                                            
                                            for agency_update in agency_updates:
                                                agency_name = agency_update["agency"]
                                                if agency_name in self.agencies_of_interest:
                                                    for link in agency_update["links"]:
                                                        try:
                                                            paragraphs = self.get_paragraphs_from_url(link)
                                                        except Exception as e:
                                                            logger.error(f"Error processing link {link}: {str(e)}")
                                                            transmittals.append(self.manual_check_required(link, metadata={"Agency": agency_name, "Date": email_date}))
                                                            continue
                                                        
                                                        metadata = {
                                                            "Agency": agency_name,
                                                            "Date": email_date
                                                        }
                                                        
                                                        transmittal = Content(
                                                            source=self.source_name,
                                                            sections=paragraphs,
                                                            url=link,
                                                            metadata=metadata
                                                        )
                                                        transmittals.append(transmittal)
                            else:
                                raise ValueError('Expected multi-part email')

            except Exception as e:
                logger.error(f'Error processing email id {email_id}: {str(e)}')
        
        return transmittals
                        
    def get_paragraphs_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # check for HTTP issues
            text = response.text
            paragraphs = self.get_paragraphs_from_text(text)
            return paragraphs
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching url {url}: {str(e)}')
            return []  # If it fails, we return an empty list

    def get_paragraphs_from_text(self, text):
        # extract main content before "supplementary information:"
        main_content = re.split(r"(?i)supplementary information:?", text, maxsplit=1)[0]
        
        # split on double newlines to get sections
        sections = re.split(r"\n\n+", main_content)
        
        # filter sections to get paragraphs with full sentences (start with capital letter and end with punctuation)
        pattern = re.compile(r'^[A-Z].*[.!?]$', re.MULTILINE)
        paragraphs = [section for section in sections if pattern.match(section.strip())]
        
        return paragraphs

    def get_links_from_text_email(self, email_body):
        # regular expression to find agency names
        agency_pattern = re.compile(r"\xa0 \*(.*?)\* \xa0")

        # regular expression to find text links
        text_link_pattern = re.compile(r"\[TEXT\]\s*\[\s*(https?://.*?)\s*\]")

        # split the email_body by agency sections
        sections = re.split(agency_pattern, email_body)[1:]

        output = []
        for i in range(0, len(sections), 2):
            agency_name = sections[i].strip()
            section_text = sections[i + 1]
            links = text_link_pattern.findall(section_text)

            output.append({"agency": agency_name, "links": links})
        return output
