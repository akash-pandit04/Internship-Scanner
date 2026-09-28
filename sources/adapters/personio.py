import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any
from sources.base import BaseSource

def _companies() -> List[Dict[str, str]]:
    import json
    from pathlib import Path
    try:
        p = Path("companies.json")
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        return data.get("personio", [])
    except Exception:
        return []

class PersonioSource(BaseSource):
    name = "personio"

    def fetch(self) -> List[Dict[str, Any]]:
        out = []
        for board_data in _companies():
            board = board_data.get("id")
            if not board:
                continue

            url = f"https://{board}.jobs.personio.de/xml"
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue

                root = ET.fromstring(r.content)
                for pos in root.findall(".//position"):
                    job_id = pos.findtext("id")
                    title = pos.findtext("name")
                    if not title:
                        continue

                    job_url = f"https://{board}.jobs.personio.de/job/{job_id}"
                    location = pos.findtext(".//office") or ""
                    
                    created = pos.findtext("createdAt")
                    if created:
                        updated_at = created
                    else:
                        updated_at = datetime.now(timezone.utc).isoformat()
                    
                    description = pos.findtext(".//jobDescriptions/jobDescription[1]/value") or ""
                    
                    record = {
                        "id": str(job_id),
                        "title": title,
                        "company": board_data.get("name", board),
                        "url": job_url,
                        "location": location,
                        "descriptionPlain": description,
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
SourceRegistry.register("personio", PersonioSource)