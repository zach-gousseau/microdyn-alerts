import re
import chardet
import email
from email.header import decode_header
import requests
from datetime import datetime, timedelta

from schemas.schemas import TextSchema
from utils.email_utils import EmailClient


class FederalRegistry:
    def __init__(self):
        self.email_client = EmailClient()
        self.federal_registry_email = "fedreg@listserv1.access.gpo.gov"

        self.agencies_of_interest = [
            "Centers for Medicare & Medicaid Services",
            # 'Centers for Disease Control and Prevention',
            "Health and Human Services Department",
            "National Institutes of Health",
            "Indian Health Services"
        ]
        
    def fetch(self, n_days=7):

        # search for recent emails 
        date_range = (datetime.now() - timedelta(days=n_days)).strftime('%d-%b-%Y')
        status, messages = self.email_client.mail.search(None, f'SINCE {date_range}')
        email_ids = messages[0].split()

        transmittals = []
        for email_id in email_ids:
            # fetch email by ID
            status, msg_data = self.email_client.mail.fetch(email_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    email_from = msg["From"]
                    email_subject = msg["Subject"]
                    email_date = msg["Date"]

                    if self.federal_registry_email in email_from:
                        
                        # decode email subject if encoded
                        decoded_subject, encoding = decode_header(email_subject)[0]
                        if isinstance(decoded_subject, bytes):
                            decoded_subject = decoded_subject.decode(encoding if encoding else "utf-8")
                        print(f"New email from {email_from}: {decoded_subject}")

                        # fetch email body
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                # decode email part payload
                                raw_payload = part.get_payload(decode=True)

                                if raw_payload:
                                    detected_encoding = chardet.detect(raw_payload)['encoding']

                                    if content_type == "text/plain" and "attachment" not in content_disposition:
                                        email_body = raw_payload.decode(detected_encoding)
                                        agency_updates = self.get_links_from_text_email(email_body)
                                        
                                        for agency_update in agency_updates:
                                            agency_name = agency_update["agency"]
                                            if agency_name in self.agencies_of_interest:
                                                for link in agency_update["links"]:
                                                    paragraphs = self.get_paragraphs_from_url(link)
                                                    
                                                    metadata = {
                                                        "Agency": agency_name,
                                                        "Date": email_date
                                                    }
                                                    
                                                    transmittal = TextSchema(
                                                        sections=paragraphs,
                                                        url=link,
                                                        metadata=metadata
                                                    )
                                                    transmittals.append(transmittal)
                                                    
                                                    

                        else:
                            raise Exception('Expected multi-part email')
        return transmittals
                        
    def get_paragraphs_from_url(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP issues
        text = response.text
        paragraphs = self.get_paragraphs_from_text(text)
        return paragraphs
        
    def get_paragraphs_from_text(self, text):
        # extract main content before "SUPPLEMENTARY INFORMATION:"
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

        # regular expression to find TEXT links
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
