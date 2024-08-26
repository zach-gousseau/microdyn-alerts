import markdown
from collections import defaultdict
from datetime import datetime, timedelta

from scrapers.cms_transmittals import CMS
from scrapers.federal_registry import FederalRegistry
from scrapers.mln import MLNNewsletter

from search.keyword_search import KeywordSearch
from search.classifier_and_summarizer import ClassifierAndSummarizer

from utils.db_utils import Writer
from utils.email_utils import EmailClient
from utils.log_config import setup_logger

logger = setup_logger(__name__)


class UpdateFinder:
    def __init__(self, n_days=7, db_path="alerts.db", email_recipients=None):
        self.content_sources = self._initialize_content_sources()
        self.keyword_search = KeywordSearch()
        self.content_analyzer = ClassifierAndSummarizer()
        self.n_days = n_days
        self.db_path = db_path
        self.email_recipients = email_recipients if email_recipients is not None else []
        self.email_client = EmailClient()

    def _initialize_content_sources(self):
        return [
            CMS(),
            FederalRegistry(),
            MLNNewsletter(),
        ]

    def _fetch_all_content(self):
        all_content = []
        for source in self.content_sources:
            try:
                content_from_source = source.fetch(n_days=self.n_days)
                all_content.extend(content_from_source)
            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
        return all_content

    def _process_content(self, content):
        keyword_search_results = self.keyword_search.find_keywords_in_paragraphs(
            content.sections
        )

        if keyword_search_results:
            relevant_sections, keywords_found = keyword_search_results
            content.keywords = keywords_found

            analysis_result = self.content_analyzer.classify_and_summarize(
                "\n".join(content.sections)
            )

            if analysis_result.is_update:
                content.summary = analysis_result.summary
                content.is_update = True

    def find_updates(self):
        all_content = self._fetch_all_content()

        # remove any duplicates
        all_content = self.remove_duplicates(all_content)

        for content in all_content:
            self._process_content(content)

        return all_content

    def remove_duplicates(self, all_content):
        return list({content.url: content for content in all_content}.values())

    def write_updates_to_db(self, content):
        new_updates = defaultdict(list)
        with Writer(db_path=self.db_path) as writer:
            for item in content:
                try:
                    source, notion_url = writer.write(item)
                except Exception as e:
                    logger.error(f"Error writing {item} to DB: {e}")

                # keep track of the notion urls for email notifications
                if item.is_update and source and notion_url:
                    new_updates[source].append(
                        {
                            "notion_url": notion_url,
                            "summary": item.summary,
                        }
                    )
        return dict(new_updates)

    def send_email_notification(self, new_updates):
        if new_updates:
            n_updates = sum([len(updates) for updates in new_updates.values()])
            start_date = datetime.now() - timedelta(days=self.n_days)
            today_date = datetime.now().strftime("%Y-%m-%d")

            # initial text
            body = f"""
            <div style="font-family: Arial, sans-serif; color: #000000;">
                <p style="color: #000000;">We have identified <strong>{n_updates} updates</strong> which may be relevant since {start_date.strftime('%Y-%m-%d')}.</p>
            """
            
            # start table
            body += """
            <p style="margin-top: 20px;">
                <a href="https://www.notion.so/ea98a7ac9e39411390d3891132aea96f" 
                style="color: #005258; text-decoration: none; font-size: 14px;"><strong>View the full table in Notion.</strong></a>
            </p>
            <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse; margin-top: 20px;">
                <thead>
                    <tr style="background-color: #f4f4f4; text-align: left;">
                        <th style="padding: 12px; border: 1px solid #ddd;">Page</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Source</th>
                        <th style="padding: 12px; border: 1px solid #ddd;">Summary</th>
                    </tr>
                </thead>
                <tbody>
            """

            # rows for each update
            for source, updates in new_updates.items():
                for update in updates:
                    body += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <a href='{update['notion_url']}' style="color: #005258; text-decoration: none;"><strong>View Update</strong></a>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{source}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{update['summary']}</td>
                    </tr>
                    """

            # end table and email body
            body += """
                </tbody>
            </table>
            <p style="margin-top: 20px; font-size: 12px; color: #777;">
                This is an automated notification. Please do not reply.
            </p>
            </div>
            """

            subject = f"Update Notification - {today_date}"
            self.email_client.send_email(
                subject, body, self.email_recipients, is_html=True
            )
            logger.info(f"Email sent to {', '.join(self.email_recipients)}")
        else:
            logger.info("No updates found, no email sent.")

    def run(self):
        content = self.find_updates()
        new_updates = self.write_updates_to_db(content)
        self.send_email_notification(new_updates)
        return content


if __name__ == "__main__":

    email_recipients = ["zachgouss@gmail.com", "zgousseau@gmail.com"]
    update_finder = UpdateFinder(
        n_days=5, db_path="alerts.db", email_recipients=email_recipients
    )
    content = update_finder.run()
