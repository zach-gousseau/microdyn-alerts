from scrapers.cms_transmittals import CMS
from scrapers.federal_registry import FederalRegistry

from search.keyword_search import KeywordSearch
from search.classifier_and_summarizer import ClassifierAndSummarizer

class UpdateFinder:
    def __init__(self):
        self.cms = CMS()
        self.federal_registry = FederalRegistry()
        
        self.keyword_search = KeywordSearch()
        self.classifier_and_summarizer = ClassifierAndSummarizer()

    def find_updates(self):
        cms_updates = self.cms.fetch()
        federal_registry_updates = self.federal_registry.fetch()
        
        all_updates = cms_updates + federal_registry_updates
        for update in all_updates:
            
            keyword_search_results = self.keyword_search.find_keywords_in_paragraphs(update.sections)
             
            if keyword_search_results is not None:
                relevant_sections, keywords_found = keyword_search_results
                response = self.classifier_and_summarizer.classify_and_summarize('\n'.join(update.sections))
                if response.is_update:
                    update.summary = response.summary
                    update.keywords = keywords_found
                else:
                    update.sections = []
            else:
                update.sections = []
        
        return [update for update in all_updates if update.sections]

    
if __name__ == '__main__':
    finder = UpdateFinder()
    updates = finder.find_updates()
    print(updates)