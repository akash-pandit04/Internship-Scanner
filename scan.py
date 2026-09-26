"""
Object-Oriented Job Scanner Engine
Refactored to meet Siemens Energy OOP requirements.
"""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import scoring
import sources

class JobCategorizer:
    """Automatically categorizes internships based on keywords."""
    def __init__(self):
        self.categories = {
            "Data & AI": ["data", "analytics", "machine learning", "ai", "artificial intelligence"],
            "Cybersecurity": ["security", "cyber", "infosec", "penetration", "crypto"],
            "Cloud/DevOps": ["cloud", "aws", "devops", "azure", "infrastructure"],
            "Hardware Engineering": ["hardware", "electrical", "systems", "circuit", "fpga"]
        }
        
    def categorize(self, title, description):
        text = f"{title} {description}".lower()
        for category, keywords in self.categories.items():
            if any(kw in text for kw in keywords):
                return category
        return "Software Engineering"  # Default

class JobScannerEngine:
    """Core Object-Oriented engine to orchestrate data aggregation."""
    def __init__(self, root_dir):
        self.root = Path(root_dir).resolve()
        self.out_file = self.root / "docs" / "data" / "jobs.json"
        self.config = self._load_config()
        self.categorizer = JobCategorizer()
        
    def _load_config(self):
        return json.loads((self.root / "config.json").read_text(encoding="utf-8-sig"))
        
    def _dedupe_key(self, title, company):
        n = lambda s: re.sub(r"[^a-z0-9]+", "", (s or "").lower())
        return f"{n(company)}|{n(title)}"
        
    def _load_previous(self):
        try:
            return json.loads(self.out_file.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {"jobs": [], "source_meta": {}}

    def _due_sources(self, meta, now):
        names = []
        for name in sources.SOURCES:
            scfg = self.config.get("sources", {}).get(name, {})
            if not scfg.get("enabled", True):
                continue
            last = (meta.get(name) or {}).get("last_run")
            if last:
                elapsed_min = (now - datetime.fromisoformat(last)).total_seconds() / 60
                if elapsed_min < scfg.get("interval_minutes", 10) * 0.85:
                    continue
            names.append(name)
        return names

    def _run_source(self, name):
        try:
            raws = sources.SOURCES[name](self.config)
            return name, raws, None
        except Exception as e:
            return name, [], f"{type(e).__name__}: {e}"

    def scan_and_aggregate(self):
        n_titles = scoring.load_titles(self.root / self.config.get("job_titles_file", "job_titles.txt"))
        print(f"Loaded {n_titles} internship titles/keywords.")

        now = datetime.now(timezone.utc)
        prev = self._load_previous()
        meta = prev.get("source_meta", {})
        jobs = {j["id"]: j for j in prev.get("jobs", [])}

        names = self._due_sources(meta, now)
        print(f"Scanning Aggregators: {', '.join(names) or '(none due)'}")

        max_h = self.config.get("store_max_age_hours", 24)
        total_new = 0

        with ThreadPoolExecutor(max_workers=6) as ex:
            results = ex.map(self._run_source, names)

        for name, raws, err in results:
            m = {"last_run": now.isoformat(), "found": 0, "new": 0, "error": err}
            if err:
                print(f"  {name}: FAILED {err}")
                m["last_run"] = (meta.get(name) or {}).get("last_run")
                meta[name] = {**(meta.get(name) or {}), "error": err}
                continue
            
            for raw in raws:
                posted = raw.get("posted_at")
                if not posted: continue
                age_h = (now - posted).total_seconds() / 3600
                if age_h > max_h or age_h < -1: continue
                
                m["found"] += 1
                sc = scoring.score_job(raw, self.config)
                
                if self.config.get("remote_only") and not sc["remote"]: continue
                if sc["score"] < self.config.get("min_score", 0): continue
                
                key = self._dedupe_key(raw["title"], raw["company"])
                if key in jobs:
                    if name != jobs[key]["source"] and name not in jobs[key]["other_sources"]:
                        jobs[key]["other_sources"].append(name)
                    continue
                
                # Auto-Categorization Feature
                category = self.categorizer.categorize(raw["title"], raw.get("description", ""))

                jobs[key] = {
                    "id": key,
                    "title": raw["title"], 
                    "company": raw["company"],
                    "location": raw["location"], 
                    "remote": sc["remote"],
                    "salary": raw.get("salary"), 
                    "salary_min": raw.get("salary_min"),
                    "url": raw.get("url") or "",
                    "source": name, 
                    "other_sources": [],
                    "description": (raw.get("description") or "")[:600],
                    "posted_at": posted.isoformat(),
                    "first_seen": now.isoformat(),
                    "score": sc["score"], 
                    "category": category, # NEW FEATURE INJECTED
                }
                m["new"] += 1
            total_new += m["new"]
            meta[name] = m
            print(f"  {name}: {m['found']} fresh internships, {m['new']} new additions.")

        # Prune older jobs
        kept = [j for j in jobs.values() if (now - datetime.fromisoformat(j["posted_at"])).total_seconds() / 3600 <= max_h]
        kept.sort(key=lambda j: j["posted_at"], reverse=True)

        out = {
            "generated_at": now.isoformat(),
            "config": {"max_age_hours": self.config.get("max_age_hours", 4)},
            "source_meta": meta,
            "jobs": kept,
        }
        self.out_file.parent.mkdir(parents=True, exist_ok=True)
        self.out_file.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Wrote {len(kept)} internship postings ({total_new} new) to dashboard data -> {self.out_file}")
        return 0

if __name__ == "__main__":
    engine = JobScannerEngine(__file__)
    sys.exit(engine.scan_and_aggregate())
