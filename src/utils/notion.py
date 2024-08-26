import requests
import json
import os
import dotenv
from schemas.schemas import Content

from utils.log_config import setup_logger

logger = setup_logger(__name__)
dotenv.load_dotenv()

class NotionClient:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.database_id = 'ea98a7ac-9e39-4113-90d3-891132aea96f'
        self.headers = {
            "Authorization": "Bearer " + self.notion_token,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        
        self.url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

    def get_pages(self, num_pages=None):
        get_all_pages = num_pages is None
        page_size = 100 if get_all_pages else num_pages

        # initialize payload for initial request
        payload = {"page_size": page_size}
        results = []

        # fetch first page
        data = self._fetch_page_data(payload)
        results.extend(data.get("results", []))

        # fetch subsequent pages
        while data.get("has_more") and get_all_pages:
            next_cursor = data.get("next_cursor")
            payload["start_cursor"] = next_cursor
            data = self._fetch_page_data(payload)
            results.extend(data.get("results", []))

        return results

    def _fetch_page_data(self, payload):
        response = requests.post(self.url, json=payload, headers=self.headers)
        return response.json()


    def add_row(self, data: Content):
        data = self.prepare_data(data)  # transform data to notion format
        create_url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": data
        }
        response = requests.post(create_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            logger.error(f"Error creating row in Notion: {response.json()}")
            
        response = json.loads(response.text)
        source = response['properties']['Source']['title'][0]['plain_text']
        url = response['url']
        return source, url

    def prepare_data(self, data: Content):
        json_data = {
            'Metadata': {'rich_text': [{'text': {'content': json.dumps(data.metadata) if data.metadata else ''}}]},
            'Keywords': {'multi_select': [{'name': keyword} for keyword in data.keywords] if data.keywords else []},
            'URL': {'url': data.url},
            'Is Update': {'checkbox': data.is_update if data.is_update else False},
            'Summary': {'rich_text': [{'text': {'content': data.summary if data.summary else ''}}]},
            'Source': {'title': [{'text': {'content': data.source}}]},
            'MANUAL CHECK REQ.': {'checkbox': data.manual_check_required if data.manual_check_required else False}
        }
        return json_data

if __name__ == '__main__':
    client = NotionClient()
    pages = client.get_pages()
    print(pages)
