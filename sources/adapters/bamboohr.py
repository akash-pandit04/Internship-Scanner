import requests
from datetime import datetime, timezone
from typing import List, Dict, Any
from sources.base import BaseSource

def _companies() -> List[Dict[str, str]]:
    import json
    from pathlib import Path
    try:
        p = Path("companies.json")
        data = json.loads(p.read_text(encoding="utf-8-sig"))
        return data.get("bamboohr", [])
    except Exception:
        return []

class BambooHRSource(BaseSource):
    name = "bamboohr"

    def fetch(self) -> List[Dict[str, Any]]:
        out = []
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0"
        }
        for board_data in _companies():
            board = board_data.get("id")
            if not board:
                continue

            url = f"https://{board}.bamboohr.com/careers/list"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    continue

                data = r.json()
                jobs = data.get("result", [])
                
                for j in jobs:
                    job_id = str(j.get("id", ""))
                    title = j.get("jobOpeningName", "")
                    if not title:
                        continue

                    location = ""
                    loc_obj = j.get("location", {})
                    if isinstance(loc_obj, dict):
                        location = loc_obj.get("city", "")

                    # BambooHR doesn't expose posted date in the list endpoint always.
                    # We default to now if missing, to let pipeline handle it.
                    updated_at = datetime.now(timezone.utc).isoformat()

                    job_url = f"https://{board}.bamboohr.com/careers/{job_id}"
                    
                    record = {
                        "id": job_id,
                        "title": title,
                        "company": board_data.get("name", board),
                        "url": job_url,
                        "location": location,
                        "descriptionPlain": "", # Need detail fetch, skip for fast list
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
SourceRegistry.register("bamboohr", BambooHRSource)
