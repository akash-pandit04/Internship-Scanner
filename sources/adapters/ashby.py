from datetime import datetime, timezone
from sources.base import BaseSource
from sources.registry import SourceRegistry
from sources.http_client import fetch_json
from sources.utils import strip_html
from sources.adapters.legacy import _companies, HEADERS

class AshbySource(BaseSource):
    def fetch(self):
        out = []
        
        for board_data in _companies("ashby"):
            board = board_data["id"]
            self.employer_stats[board] = {"status": "HEALTHY"}
            try:
                # We'll use the pagination abstraction just to satisfy Step 5, 
                # although public Ashby job boards often return all jobs at once.
                def fetch_page(token):
                    url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
                    # Ashby doesn't have a standard public pagination cursor on this endpoint, 
                    # but if it did, we'd pass it here.
                    return fetch_json(url, headers=HEADERS)
                
                def extract_jobs(resp):
                    return resp.get("jobs", [])
                    
                def next_page(resp):
                    # No standard pagination cursor on the unauthenticated board API.
                    return None

                jobs = self.paginate(fetch_page, extract_jobs, next_page, max_pages=1)
                
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"ashby/{board} failed: {e}")
                self.employer_stats[board] = {"status": "BROKEN"}
                continue
                
            for j in jobs:
                if isinstance(j, str):
                    import logging
                    logging.getLogger(__name__).error(f"ashby jobs yielded a string! board: {board}, j: {j}")
                    continue
                try:
                    posted_str = j.get("publishedAt")
                    if not posted_str:
                        continue
                    posted = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    continue
                    
                loc = j.get("location")
                if isinstance(loc, str):
                    loc_name = loc
                elif isinstance(loc, dict):
                    loc_name = loc.get("name") or "Remote"
                else:
                    loc_name = "Remote"
                    
                is_remote = bool(j.get("isRemote")) or "remote" in loc_name.lower()
                
                emp_type = j.get("employmentType") or ""
                
                out.append({
                    "title": j.get("title") or "",
                    "company": board.replace("-", " ").title(),
                    "location": loc_name,
                    "remote": is_remote,
                    "salary": None,
                    "salary_min": None,
                    "url": j.get("jobUrl") or "",
                    "description": strip_html(j.get("descriptionPlain") or j.get("descriptionHtml") or "")[:1200],
                    "employment_type": emp_type,
                    "posted_at": posted,
                    "employer_id": board, "employer_ats": "ashby"
                })
                
        return out

SourceRegistry.register("ashby", AshbySource)
