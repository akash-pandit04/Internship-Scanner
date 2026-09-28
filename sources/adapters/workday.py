import requests
import json
from typing import List, Dict, Any
from sources.base import BaseSource

def _companies() -> List[Dict[str, str]]:
    from pathlib import Path
    try:
        p = Path("companies.json")
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        return data.get("workday", [])
    except Exception:
        return []

class WorkdaySource(BaseSource):
    """
    Workday adapter using legitimately configured employer RaaS (Report-as-a-Service) feeds.
    Does NOT scrape internal /wday/cxs endpoints.
    Requires companies.json to supply 'host', 'tenant', and 'report_name' for public feeds.
    """
    name = "workday"

    def fetch(self) -> List[Dict[str, Any]]:
        out = []
        headers = {"User-Agent": "Mozilla/5.0"}
        for board_data in _companies():
            host = board_data.get("host")
            tenant = board_data.get("tenant")
            report_name = board_data.get("report_name")
            
            if not host or not tenant or not report_name:
                continue

            # RaaS JSON endpoint
            url = f"https://{host}/{tenant}/d/raas/report/{tenant}/{report_name}?format=json"
                
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue

                data = r.json()
                jobs = data.get("Report_Entry", [])
                
                for j in jobs:
                    # Workday RaaS column names depend on the report config
                    # We look for common aliases: Job_Requisition, Title, URL, Location
                    title = j.get("title", j.get("Title", j.get("Job_Title", "")))
                    if not title:
                        continue
                        
                    job_id = j.get("id", j.get("Requisition_ID", title))
                    job_url = j.get("url", j.get("URL", ""))
                    updated_at = j.get("posted_on", j.get("Posted_Date", ""))
                    location = j.get("location", j.get("Location", ""))
                    
                    record = {
                        "id": str(job_id),
                        "title": title,
                        "company": board_data.get("name", tenant),
                        "url": job_url,
                        "location": location,
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
SourceRegistry.register("workday", WorkdaySource)
