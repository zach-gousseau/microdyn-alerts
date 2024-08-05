import imaplib
from email.header import decode_header
import dotenv
import os

dotenv.load_dotenv()

class EmailClient():
    def __init__(self):
        self.username = os.getenv('EMAIL_ADDRESS')
        self.app_password = os.getenv('EMAIL_APP_PASSWORD')

        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")  # connect to gmail IMAP server

        self.mail.login(self.username, self.app_password)
        self.mail.select("inbox")