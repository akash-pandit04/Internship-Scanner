import json
from pathlib import Path
from datetime import datetime, timezone
import email.utils
import xml.etree.ElementTree as ET

from sources.base import BaseSource
from sources.registry import SourceRegistry
from sources.http_client import fetch_json, fetch_text
from sources.utils import strip_html, html_to_markdown, format_salary

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
ROOT = Path(__file__).resolve().parent.parent.parent

class RemoteOKSource(BaseSource):
    def fetch(self):
        out = []
        # Uses fetch_json which automatically handles rate limits and retries
        data = fetch_json("https://remoteok.com/api", headers=HEADERS)
        for j in data:
            if not isinstance(j, dict) or not j.get("position"):
                continue
            try:
                posted = datetime.fromisoformat(str(j["date"]).replace("Z", "+00:00"))
            except (KeyError, ValueError):
                continue
            smin = j.get("salary_min") or None
            out.append({
                "title": j["position"], "company": j.get("company") or "",
                "location": j.get("location") or "Remote", "remote": True,
                "salary": format_salary(smin, j.get("salary_max")),
                "salary_min": int(smin) if smin else None,
                "url": j.get("url") or "",
                "description": html_to_markdown(j.get("description") or ""),
                "posted_at": posted,
            })
        return out

class RemotiveSource(BaseSource):
    def fetch(self):
        out = []
        data = fetch_json("https://remotive.com/api/remote-jobs?limit=100", headers=HEADERS)
        for j in data.get("jobs", []):
            try:
                posted = datetime.fromisoformat(j["publication_date"])
            except (KeyError, ValueError):
                continue
            if posted.tzinfo is None:
                posted = posted.replace(tzinfo=timezone.utc)
            out.append({
                "title": j.get("title") or "", "company": j.get("company_name") or "",
                "location": j.get("candidate_required_location") or "Remote",
                "remote": True, "salary": j.get("salary") or None, "salary_min": None,
                "url": j.get("url") or "",
                "description": html_to_markdown(j.get("description") or ""),
                "posted_at": posted,
            })
        return out

class JobicySource(BaseSource):
    def fetch(self):
        out = []
        data = fetch_json("https://jobicy.com/api/v2/remote-jobs?count=100&geo=usa", headers=HEADERS)
        for j in data.get("jobs", []):
            try:
                posted = datetime.fromisoformat(str(j["pubDate"]).replace("Z", "+00:00"))
            except (KeyError, ValueError):
                continue
            if posted.tzinfo is None:
                posted = posted.replace(tzinfo=timezone.utc)
            smin = j.get("annualSalaryMin") or None
            out.append({
                "title": j.get("jobTitle") or "", "company": j.get("companyName") or "",
                "location": j.get("jobGeo") or "Remote", "remote": True,
                "salary": format_salary(smin, j.get("annualSalaryMax")),
                "salary_min": int(smin) if smin else None,
                "url": j.get("url") or "",
                "description": html_to_markdown(j.get("jobExcerpt") or j.get("jobDescription") or ""),
                "posted_at": posted,
            })
        return out

class WeWorkRemotelySource(BaseSource):
    def fetch(self):
        out = []
        xml_data = fetch_text("https://weworkremotely.com/remote-jobs.rss", headers=HEADERS)
        root = ET.fromstring(xml_data)
        for item in root.iter("item"):
            raw_title = item.findtext("title") or ""
            company, sep, title = raw_title.partition(": ")
            if not sep:
                company, title = "", raw_title
            try:
                posted = email.utils.parsedate_to_datetime(item.findtext("pubDate") or "")
            except (TypeError, ValueError):
                continue
            out.append({
                "title": title.strip(), "company": company.strip(),
                "location": (item.findtext("region") or "Remote").strip(),
                "remote": True, "salary": None, "salary_min": None,
                "url": (item.findtext("link") or "").strip(),
                "description": html_to_markdown(item.findtext("description") or ""),
                "posted_at": posted,
            })
        return out

def _companies(kind):
    try:
        data = json.loads((ROOT / "companies.json").read_text(encoding="utf-8-sig")).get(kind, [])
        out = []
        for item in data:
            if isinstance(item, dict):
                if item.get("enabled", True):
                    out.append(item)
            else:
                out.append({"id": item, "name": item.replace('-', ' ').title(), "region": "Global", "enabled": True})
        return out
    except FileNotFoundError:
        return []

class GreenhouseSource(BaseSource):
    def fetch(self):
        # We need the global config's max_age_hours
        retention_days = self.config.get("global", {}).get("retention_days", 30)
        now = datetime.now(timezone.utc)
        out = []
        for board_data in _companies("greenhouse"):
            board = board_data["id"]
            self.employer_stats[board] = {"status": "HEALTHY"}
            board_name = board_data.get("name") or board.replace('-', ' ').title()
            try:
                data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", headers=HEADERS)
                jobs = data.get("jobs", [])
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"greenhouse/{board}: {e}")
                self.employer_stats[board] = {"status": "BROKEN"}
                continue
            fresh = []
            for j in jobs:
                try:
                    upd = datetime.fromisoformat(j["updated_at"])
                except (KeyError, ValueError):
                    continue
                if (now - upd).total_seconds() / 86400 <= retention_days:
                    fresh.append((j, upd))
            for j, upd in fresh[:15]:
                desc = ""
                try:
                    detail = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{j['id']}", headers=HEADERS)
                    desc = html_to_markdown(detail.get("content") or "")
                except Exception:
                    pass
                out.append({
                    "title": j.get("title") or "",
                    "company": board_name,
                    "location": (j.get("location") or {}).get("name") or "",
                    "remote": None,
                    "salary": None, "salary_min": None,
                    "url": j.get("absolute_url") or "",
                    "description": desc, "posted_at": upd,
                    "employer_id": board, "employer_ats": "greenhouse"
                })
        return out

class LeverSource(BaseSource):
    def fetch(self):
        retention_days = self.config.get("global", {}).get("retention_days", 30)
        now = datetime.now(timezone.utc)
        out = []
        for board_data in _companies("lever"):
            c = board_data["id"]
            self.employer_stats[c] = {"status": "HEALTHY"}
            board_name = board_data.get("name") or c.replace('-', ' ').title()
            try:
                jobs = fetch_json(f"https://api.lever.co/v0/postings/{c}?mode=json&limit=100", headers=HEADERS)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"lever/{c}: {e}")
                self.employer_stats[c] = {"status": "BROKEN"}
                continue
            if not isinstance(jobs, list):
                continue
            for j in jobs:
                try:
                    posted = datetime.fromtimestamp(j["createdAt"] / 1000, tz=timezone.utc)
                except (KeyError, TypeError, ValueError):
                    continue
                if (now - posted).total_seconds() / 86400 > retention_days:
                    continue
                loc = (j.get("categories") or {}).get("location") or ""
                out.append({
                    "title": j.get("text") or "", "company": board_name,
                    "location": loc,
                    "remote": j.get("workplaceType") == "remote" or "remote" in loc.lower(),
                    "salary": None, "salary_min": None,
                    "url": j.get("hostedUrl") or "",
                    "description": html_to_markdown(j.get("descriptionPlain") or ""),
                    "posted_at": posted,
                    "employer_id": c, "employer_ats": "lever"
                })
        return out

class ArbeitnowSource(BaseSource):
    def fetch(self):
        out = []
        data = fetch_json("https://www.arbeitnow.com/api/job-board-api", headers=HEADERS)
        for j in data.get("data", []):
            try:
                posted = datetime.fromtimestamp(j["created_at"], tz=timezone.utc)
            except (KeyError, TypeError, ValueError):
                continue
            emp_type = ""
            if j.get("job_types"):
                emp_type = ", ".join(j["job_types"])
            out.append({
                "title": j.get("title") or "", 
                "company": j.get("company_name") or "",
                "location": j.get("location") or "Remote", 
                "remote": bool(j.get("remote")),
                "salary": None, 
                "salary_min": None,
                "url": j.get("url") or "",
                "description": html_to_markdown(j.get("description") or ""),
                "employment_type": emp_type,
                "posted_at": posted,
            })
        return out

# Register adapters
SourceRegistry.register('remoteok', RemoteOKSource)
SourceRegistry.register('remotive', RemotiveSource)
SourceRegistry.register('jobicy', JobicySource)
SourceRegistry.register('weworkremotely', WeWorkRemotelySource)
SourceRegistry.register('greenhouse', GreenhouseSource)
SourceRegistry.register('lever', LeverSource)
SourceRegistry.register('arbeitnow', ArbeitnowSource)
