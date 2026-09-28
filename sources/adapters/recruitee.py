import requests
from typing import List, Dict, Any
from sources.base import BaseSource

def _companies() -> List[Dict[str, str]]:
    import json
    from pathlib import Path
    try:
        p = Path("companies.json")
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        return data.get("recruitee", [])
    except Exception:
        return []

class RecruiteeSource(BaseSource):
    name = "recruitee"

    def fetch(self) -> List[Dict[str, Any]]:
        out = []
        headers = {"User-Agent": "Mozilla/5.0"}
        for board_data in _companies():
            board = board_data.get("id")
            if not board:
                continue

            url = f"https://{board}.recruitee.com/api/offers"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue

                data = r.json()
                jobs = data.get("offers", [])
                
                for j in jobs:
                    job_id = str(j.get("id", ""))
                    title = j.get("title", "")
                    if not title:
                        continue

                    location = j.get("location", "") or ""
                    updated_at = j.get("published_at") or j.get("created_at")
                    job_url = j.get("careers_url", "")
                    
                    record = {
                        "id": job_id,
                        "title": title,
                        "company": board_data.get("name", board),
                        "url": job_url,
                        "location": location,
                        "descriptionPlain": "", # HTML in description
                        "publishedAt": updated_at,
                        "remote": j.get("remote", False)
                    }
                    out.append(record)
            except Exception:
                pass
                
        return self.normalize(out)

    def normalize(self, raw_jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for j in raw_jobs:
            remote_val = j.get("remote", False)
            normalized.append({
                "id": j["id"],
                "title": j["title"],
                "company": j["company"],
                "url": j["url"],
                "location": j["location"],
                "remote": remote_val or "remote" in j["location"].lower() or "remote" in j["title"].lower(),
                "posted_at": j["publishedAt"],
                "updated_at": j["publishedAt"],
                "source": self.name
            })
        return normalized

from sources.registry import SourceRegistry
SourceRegistry.register("recruitee", RecruiteeSource)
