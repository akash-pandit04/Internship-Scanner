import requests
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from sources.base import BaseSource

def _companies() -> List[Dict[str, str]]:
    from pathlib import Path
    try:
        p = Path("companies.json")
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        return data.get("jobvite", [])
    except Exception:
        return []

class JobviteSource(BaseSource):
    """
    Jobvite adapter using officially configured XML feeds.
    Requires companies.json to supply 'company_id' or a direct 'feed_url'.
    """
    name = "jobvite"

    def fetch(self) -> List[Dict[str, Any]]:
        out = []
        headers = {"User-Agent": "Mozilla/5.0"}
        for board_data in _companies():
            feed_url = board_data.get("feed_url")
            company_id = board_data.get("company_id")
            
            if not feed_url and not company_id:
                continue
                
            url = feed_url or f"https://app.jobvite.com/CompanyJobs/Xml.aspx?c={company_id}"
                
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue

                # If it's a redirect to HTML, skip
                if "<html" in r.text.lower()[:100]:
                    continue

                root = ET.fromstring(r.content)
                jobs = root.findall(".//job")
                
                for j in jobs:
                    job_id = j.findtext("id", "")
                    title = j.findtext("title", "")
                    if not title:
                        continue
                        
                    job_url = j.findtext("detail-url", "")
                    updated_at = j.findtext("date", "")
                    
                    record = {
                        "id": job_id,
                        "title": title,
                        "company": board_data.get("name", ""),
                        "url": job_url,
                        "location": j.findtext("location", ""),
                        "descriptionPlain": "",
                        "publishedAt": updated_at
                    }
                    out.append(record)
            except Exception:
                pass
                
        return self.normalize(out)

    def normalize(self, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for j in raw_jobs:
            normalized.append({
                "id": j["id"],
                "title": j["title"],
                "company": j["company"],
                "url": j["url"],
                "location": j["location"],
                "remote": "remote" in j["location"].lower() or "remote" in j["title"].lower(),
                "posted_at": j["publishedAt"],
                "updated_at": j["publishedAt"],
                "source": self.name
            })
        return normalized

from sources.registry import SourceRegistry
SourceRegistry.register("jobvite", JobviteSource)
