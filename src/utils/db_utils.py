import sqlite3
import json
import logging
from typing import Optional
from schemas.schemas import Content
from utils.notion import NotionClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Writer:
    def __init__(self, db_path: str = 'alerts.db'):
        self.connection = sqlite3.connect(db_path)  # sqlite connection
        self.notion_client = NotionClient()  # notion client
        
    def write_notion(self, content: Content):
        # write content to notion
        try:
            return self.notion_client.add_row(content)
        except Exception as e:
            logger.error(f"failed to write to notion: {e}")
            return None

    def content_exists(self, url: str) -> bool:
        cursor = self.connection.cursor()
        try:
            query = "SELECT 1 FROM content WHERE url = ? LIMIT 1"
            cursor.execute(query, (url,))
            result = cursor.fetchone()
            return result is not None
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error: {e}")
            return False
        finally:
            cursor.close()  # Ensure cursor is closed

    def write_sqlite(self, content: Content):
        # insert content into the content table
        try:
            content_query = """
            INSERT INTO content (source, text, url, summary, keywords, is_update, manual_check_required)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            content_data = (
                content.source,  # source
                '\n'.join(content.sections),  # text
                content.url,  # url
                content.summary,  # summary
                ', '.join(content.keywords) if content.keywords else None,  # keywords
                content.is_update,  # is update
                content.manual_check_required,  # manual check required
            )
            cursor = self.connection.cursor()
            try:
                cursor.execute(content_query, content_data)
                
                # get the last inserted content_id for the metadata table
                content_id = cursor.lastrowid

                # insert metadata entries if any exist
                if content.metadata:
                    metadata_query = """
                    INSERT INTO metadata (content_id, key, value)
                    VALUES (?, ?, ?)
                    """
                    metadata_data = [(content_id, key, value) for key, value in content.metadata.items()]
                    cursor.executemany(metadata_query, metadata_data)

                # commit the transaction
                self.connection.commit()
            except sqlite3.DatabaseError as e:
                logger.error(f"Database error: {e}")
                self.connection.rollback()  # rollback on failure
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            finally:
                cursor.close()  # ensure cursor is closed

        except Exception as e:
            logger.error(f"Unexpected error: {e}")

    def write(self, content: Content):
        # check if content exists, if not, write it to sqlite and notion
        if self.content_exists(content.url):
            logger.info(f"Content with url '{content.url}' already exists. Skipping write.")
            return None, None
        self.write_sqlite(content)
        source, notion_link = self.write_notion(content)
        return source, notion_link
        
    def close(self):
        # close the sqlite connection
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # ensure the connection is closed when the instance is exited
        self.close()
        return False
