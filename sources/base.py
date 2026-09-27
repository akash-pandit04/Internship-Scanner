from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSource(ABC):
    """
    Base class for all internship sources.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__.lower().replace("source", "")
        # Standard configs
        self.enabled = self.config.get("enabled", True)
        self.max_pages = self.config.get("max_pages", 5)

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch and normalize jobs from the source.
        Returns a list of standardized job dictionaries.
        """
        pass

    def paginate(self, fetch_page_func, extract_data_func, next_page_func, max_pages=None) -> List[Dict[str, Any]]:
        """
        Reusable pagination mechanism.
        fetch_page_func(page_token) -> response object
        extract_data_func(response) -> list of raw items
        next_page_func(response) -> next page_token or None
        """
        max_p = max_pages or self.max_pages
        all_items = []
        page_token = None
        
        for _ in range(max_p):
            try:
                resp = fetch_page_func(page_token)
                items = extract_data_func(resp)
                
                if not items:
                    break
                    
                all_items.extend(items)
                page_token = next_page_func(resp)
                
                if not page_token:
                    break
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Pagination error in {self.name}: {e}")
                break
                
        return all_items
