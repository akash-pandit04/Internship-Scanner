from datetime import datetime, timezone
from sources.base import BaseSource
from sources.registry import SourceRegistry
from sources.http_client import fetch_json
from sources.adapters.legacy import _companies, HEADERS

class SmartRecruitersSource(BaseSource):
    def fetch(self):
        out = []
        
        for board_data in _companies("smartrecruiters"):
            board = board_data["id"]
            self.employer_stats[board] = {"status": "HEALTHY"}
            try:
                def fetch_page(token):
                    offset = token or 0
                    url = f"https://api.smartrecruiters.com/v1/companies/{board}/postings?limit=100&offset={offset}"
                    return fetch_json(url, headers=HEADERS)
                
                def extract_jobs(resp):
                    return resp.get("content", [])
                    
                def next_page(resp):
                    offset = resp.get("offset", 0)
                    limit = resp.get("limit", 100)
                    total = resp.get("totalFound", 0)
                    next_offset = offset + limit
                    if next_offset < total:
                        return next_offset
                    return None

                jobs = self.paginate(fetch_page, extract_jobs, next_page)
                
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"smartrecruiters/{board} failed: {e}")
                self.employer_stats[board] = {"status": "BROKEN"}
                continue
                
            for j in jobs:
                if isinstance(j, str):
                    continue
                try:
                    posted_str = j.get("releasedDate")
                    if not posted_str:
                        continue
                    posted = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    continue
                    
                loc_obj = j.get("location") or {}
                loc_name = loc_obj.get("fullLocation") or loc_obj.get("city") or "Remote"
                is_remote = bool(loc_obj.get("remote")) or "remote" in loc_name.lower()
                
                emp_type_obj = j.get("typeOfEmployment") or {}
                emp_type = emp_type_obj.get("label") or emp_type_obj.get("id") or ""
                
                # URL construction
                job_id = j.get("id", "")
                url = f"https://jobs.smartrecruiters.com/{board}/{job_id}"
                
                out.append({
                    "title": j.get("name") or "",
                    "company": board.replace("-", " ").title(),
                    "location": loc_name,
                    "remote": is_remote,
                    "salary": None,
                    "salary_min": None,
                    "url": url,
                    "description": "", # List API does not provide description, rely on title/employment_type
                    "employment_type": emp_type,
                    "posted_at": posted,
                    "employer_id": board, "employer_ats": "smartrecruiters"
                })
                
        return out

SourceRegistry.register("smartrecruiters", SmartRecruitersSource)
