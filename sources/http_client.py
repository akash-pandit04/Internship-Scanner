import time
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    pass

def fetch_json(url: str, headers: Dict[str, str] = None, max_retries: int = 3, timeout: int = 15) -> Any:
    """
    HTTP GET requesting JSON with exponential backoff for 429 and 5xx errors.
    """
    delay = 2
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            
            if resp.status_code == 429:
                if attempt == max_retries:
                    raise RateLimitError(f"Rate limited on {url} after {max_retries} retries")
                logger.warning(f"429 Rate limited on {url}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue
                
            resp.raise_for_status()
            return resp.json()
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                logger.error(f"Failed to fetch {url}: {e}")
                raise
            logger.warning(f"Request failed for {url}: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
    
    raise Exception(f"Failed to fetch {url} after {max_retries} retries")

def fetch_text(url: str, headers: Dict[str, str] = None, max_retries: int = 3, timeout: int = 15) -> str:
    """
    HTTP GET requesting text (e.g., XML/RSS) with exponential backoff.
    """
    delay = 2
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            
            if resp.status_code == 429:
                if attempt == max_retries:
                    raise RateLimitError(f"Rate limited on {url} after {max_retries} retries")
                logger.warning(f"429 Rate limited on {url}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
                continue
                
            resp.raise_for_status()
            return resp.text
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries:
                logger.error(f"Failed to fetch {url}: {e}")
                raise
            logger.warning(f"Request failed for {url}: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
            
    raise Exception(f"Failed to fetch {url} after {max_retries} retries")

