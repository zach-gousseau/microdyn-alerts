from abc import ABC, abstractmethod
from schemas.schemas import Content

class DataSource(ABC):
    def __init__(self):
        self.source_name = None
        
    def manual_check_required(self, url, metadata=None):
        return Content(
            source=self.source_name,
            sections=[],
            url=url,
            summary="Scraper failed; manual check required.",
            manual_check_required=True,
            metadata=metadata
        )
    
    @abstractmethod
    def fetch(self, n_days=7):
        pass