import urllib.request
import json
import logging
from datetime import datetime, timezone
from typing import Iterator, Dict, Any, Optional

from sources.base import BaseSource
from schema import JobRecord

logger = logging.getLogger(__name__)

class TheMuseSource(BaseSource):
    name = "themuse"

    def fetch(self) -> list:
        return []
        self.api_key = self.config.get("api_key")
            
        all_jobs = []
        page = 0
        max_pages = self.max_pages if self.max_pages else 500
        
        while page <= max_pages:
            url = f"https://www.themuse.com/api/public/jobs?page={page}&level=Internship"
            if self.api_key and self.api_key != 'mock_key_for_testing':
                url += f"&api_key={self.api_key}"
                
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                logger.info(f"TheMuseSource fetching page {page}...")
                resp = urllib.request.urlopen(req)
                data = json.loads(resp.read().decode('utf-8'))
                
                results = data.get('results', [])
                if not results:
                    break
                    
                for raw_job in results:
                    all_jobs.append(self.normalize(raw_job))
                    
                page_count = data.get('page_count', 0)
                if page >= page_count:
                    break
                page += 1
                
            except urllib.error.HTTPError as e:
                logger.error(f"HTTP Error {e.code} on page {page} (possibly rate limit or bad key): {e.reason}")
                break
            except Exception as e:
                logger.error(f"Failed to fetch TheMuse page {page}: {e}")
                break
                
        return all_jobs

    def normalize(self, raw_job: Dict[str, Any]) -> dict:
        locations = raw_job.get("locations", [])
        loc_str = locations[0].get("name", "Unknown") if locations else "Unknown"
        
        company = raw_job.get("company", {}).get("name", "Unknown")
        
        # parse 2024-04-12T12:00:00Z
        published_at_str = raw_job.get("publication_date")
        posted_at = None
        if published_at_str:
            try:
                # Muse uses e.g. 2022-09-02T16:11:59.273767Z
                if '.' in published_at_str:
                    published_at_str = published_at_str.split('.')[0] + 'Z'
                posted_at = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
                
        return {
            "source": self.name,
            "id": str(raw_job.get("id")),
            "title": raw_job.get("name", ""),
            "company": company,
            "url": raw_job.get("refs", {}).get("landing_page") or raw_job.get("refs", {}).get("short") or "",
            "location": loc_str,
            "employment_type": "Internship",
            "remote": "remote" in loc_str.lower(),
            "description": raw_job.get("contents", "")[:300] + ("..." if len(raw_job.get("contents", "")) > 300 else ""),
            "posted_at": posted_at,
        }

from sources.registry import SourceRegistry
SourceRegistry.register('themuse', TheMuseSource)
