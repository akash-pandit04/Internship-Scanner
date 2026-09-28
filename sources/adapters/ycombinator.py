import json
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from sources.base import BaseSource
from sources.registry import SourceRegistry
from sources.http_client import fetch_text
from sources.adapters.legacy import HEADERS

logger = logging.getLogger(__name__)

class YCombinatorSource(BaseSource):
    # Base roles and locations derived from YC jobs filters
    ROLES = [
        'software-engineer', 'designer', 'product-manager', 
        'recruiting-hr', 'sales-manager', 'marketing', 
        'support', 'operations', 'science'
    ]
    LOCATIONS = [
        'san-francisco', 'new-york', 'los-angeles', 
        'seattle', 'austin', 'chicago', 'india', 'remote'
    ]

    def fetch(self):
        out = []
        seen_ids = set()
        
        # Scrape combinations of roles and locations to maximize unique job discovery
        # YC jobs page only exposes a limited slice of jobs per SEO category
        
        # 1. First fetch all roles globally
        for role in self.ROLES:
            url = f"https://www.ycombinator.com/jobs/role/{role}"
            self._scrape_page(url, out, seen_ids)
            
        # 2. Then fetch cross-product of roles and locations
        for role in self.ROLES:
            for loc in self.LOCATIONS:
                url = f"https://www.ycombinator.com/jobs/role/{role}/{loc}"
                self._scrape_page(url, out, seen_ids)
                
        return out

    def _scrape_page(self, url, out, seen_ids):
        try:
            resp = fetch_text(url, headers=HEADERS)
            soup = BeautifulSoup(resp, 'html.parser')
            node = soup.find(attrs={'data-page': True})
            
            if not node:
                logger.warning(f"[ycombinator] No data-page attribute found on {url}")
                return
                
            data = json.loads(node['data-page'])
            jobs = data.get('props', {}).get('jobPostings', [])
            
            for j in jobs:
                jid = str(j.get('id', ''))
                if jid in seen_ids:
                    continue
                seen_ids.add(jid)
                out.append(self.normalize(j))
                
        except Exception as e:
            logger.error(f"[ycombinator] Failed to fetch {url}: {e}")
            
    def _parse_relative_date(self, text: str):
        if not text:
            return None
        import re
        from datetime import timedelta
        text = text.lower().replace('about ', '').replace('over ', '').replace('almost ', '')
        match = re.search(r'(\d+)\s+(hour|day|month|year)', text)
        if not match:
            return None
        val = int(match.group(1))
        unit = match.group(2)
        now = datetime.now(timezone.utc)
        if unit == 'hour':
            return now - timedelta(hours=val)
        elif unit == 'day':
            return now - timedelta(days=val)
        elif unit == 'month':
            return now - timedelta(days=val*30)
        elif unit == 'year':
            return now - timedelta(days=val*365)
        return None

    def normalize(self, raw: dict) -> dict:
        url = raw.get('applyUrl') or raw.get('url', '')
        if url and not url.startswith('http'):
            url = f"https://www.ycombinator.com{url}"
            
        return {
            "title": raw.get("title", ""),
            "company": raw.get("companyName", "Unknown"),
            "location": raw.get("location", ""),
            "remote": 'remote' in raw.get("location", "").lower(),
            "salary": raw.get("salaryRange"),
            "salary_min": None,
            "url": url,
            "description": raw.get("companyOneLiner", ""),
            "employment_type": raw.get("type", ""),
            "posted_at": self._parse_relative_date(raw.get("createdAt")),
        }

SourceRegistry.register("ycombinator", YCombinatorSource)
