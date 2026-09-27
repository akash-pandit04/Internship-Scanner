import json
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

import scoring
import sources
from eligibility import determine_eligibility, EligibilityStatus
from schema import validate_job_schema, JobRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class JobCategorizer:
    def __init__(self):
        self.categories = {
            "Data & AI": ["data", "analytics", "machine learning", "ai", "artificial intelligence"],
            "Cybersecurity": ["security", "cyber", "infosec", "penetration", "crypto"],
            "Cloud/DevOps": ["cloud", "aws", "devops", "azure", "infrastructure"],
            "Hardware Engineering": ["hardware", "electrical", "systems", "circuit", "fpga"]
        }
        
    def categorize(self, title: str, description: str) -> List[str]:
        text = f"{title} {description}".lower()
        cats = []
        for category, keywords in self.categories.items():
            if any(kw in text for kw in keywords):
                cats.append(category)
        if not cats:
            cats.append("Software Engineering")
        return cats

class InternshipScannerPipeline:
    def __init__(self, root_dir):
        self.root = Path(root_dir).resolve()
        self.out_file = self.root / "docs" / "data" / "jobs.json"
        self.config = self._load_config()
        self.categorizer = JobCategorizer()
        
    def _load_config(self) -> Dict[str, Any]:
        try:
            return json.loads((self.root / "config.json").read_text(encoding="utf-8-sig"))
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("No config.json found or invalid JSON. Using empty config.")
            return {}

    def fingerprint(self, job: Dict[str, Any]) -> str:
        """Deterministic deduplication fingerprint."""
        company = str(job.get("company", "")).strip().lower()
        title = str(job.get("title", "")).strip().lower()
        # Keep it simple and stable: company + title is usually enough. URL might change slightly.
        # But user requested: company + title + location + application URL
        location = str(job.get("location", "")).strip().lower()
        url = str(job.get("url", "")).strip().lower()
        
        raw_fp = f"{company}|{title}|{location}|{url}"
        return re.sub(r"[^a-z0-9]+", "_", raw_fp)
        
    def is_fresh(self, raw_job: dict, now: datetime) -> bool:
        max_age_hours = self.config.get("max_age_hours", 24)
        posted_at = raw_job.get("posted_at")
        if not posted_at:
            return True # missing dates are accepted
        try:
            age = now - posted_at
            return age.total_seconds() <= (max_age_hours * 3600)
        except Exception:
            return True # malformed handled safely

    def fetch_source(self, name: str, fetch_func) -> List[Dict[str, Any]]:
        logging.info(f"Fetching from {name}...")
        try:
            raws = fetch_func(self.config)
            for r in raws:
                r["source"] = name
            return raws
        except Exception as e:
            logging.error(f"Source {name} failed: {type(e).__name__}: {e}")
            return []

    def run(self):
        logging.info("Starting internship scanner pipeline...")
        scoring.load_titles(self.root / self.config.get("job_titles_file", "job_titles.txt"))
        
        raw_jobs = []
        now = datetime.now(timezone.utc)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for name, func in sources.SOURCES.items():
                if self.config.get("sources", {}).get(name, {}).get("enabled", True):
                    futures.append(executor.submit(self.fetch_source, name, func))
            for future in futures:
                res = future.result()
                if isinstance(res, list):
                    raw_jobs.extend(res)
                else:
                    logging.error(f"Source adapter returned non-list: {type(res)}")
                
        logging.info(f"Fetched {len(raw_jobs)} raw records across all sources.")
        
        processed_jobs: Dict[str, JobRecord] = {}
        rejected_jobs = []
        metrics = {
            "fetched": len(raw_jobs),
            "normalized": 0,
            "schema_rejected": 0,
            "stale_rejected": 0,
            "non_internship": 0,
            "uncertain": 0,
            "accepted": 0,
            "deduplicated": 0
        }
        
        for raw in raw_jobs:
            # 1. Normalize
            if "description" not in raw:
                raw["description"] = ""
            if "employment_type" not in raw:
                raw["employment_type"] = ""
            metrics["normalized"] += 1
                
            # 2. Schema Validation
            if not validate_job_schema(raw):
                metrics["schema_rejected"] += 1
                rejected_jobs.append({"reason": "schema", "job": raw})
                continue
                
            # 2.5 Freshness Filtering
            if not self.is_fresh(raw, now):
                metrics["stale_rejected"] += 1
                rejected_jobs.append({"reason": "stale", "job": raw})
                continue
                
            # 3. Eligibility
            eligibility = determine_eligibility(raw["title"], raw["description"], raw["employment_type"])
            if eligibility == EligibilityStatus.NON_INTERNSHIP:
                metrics["non_internship"] += 1
                rejected_jobs.append({"reason": "non_internship", "job": raw})
                continue
            elif eligibility == EligibilityStatus.UNCERTAIN:
                metrics["uncertain"] += 1
                rejected_jobs.append({"reason": "uncertain", "job": raw})
                continue
                
            # 4. Categorization
            cats = self.categorizer.categorize(raw["title"], raw["description"])
            
            # 5. Scoring
            score_data = scoring.score_job(raw, self.config)
            
            # 6. Deduplication
            fp = self.fingerprint(raw)
            if fp in processed_jobs:
                metrics["deduplicated"] += 1
                rejected_jobs.append({"reason": "duplicate", "job": raw})
                continue
                
            record = JobRecord(
                id=fp,
                title=raw["title"],
                company=raw["company"],
                location=raw["location"],
                remote=raw.get("remote", False) or score_data.get("remote", False),
                employment_type=raw["employment_type"],
                description=raw["description"],
                url=raw["url"],
                source=raw["source"],
                posted_at=raw["posted_at"],
                fetched_at=now,
                categories=cats,
                skills=[],
                score=score_data["score"]
            )
            processed_jobs[fp] = record
            metrics["accepted"] += 1
            
        logging.info(f"Metrics: {metrics}")
        logging.info(f"Pipeline complete. Yielded {len(processed_jobs)} valid unique internships.")
        
        # Save output
        out_data = {
            "generated_at": now.isoformat(),
            "config": {"max_age_hours": self.config.get("max_age_hours", 24)},
            "source_meta": {},
            "jobs": [j.to_dict() for j in processed_jobs.values()]
        }
        
        # Dump rejected for analysis
        (self.root / "rejected_analysis.json").write_text(
            json.dumps([{**r, "job": {k: str(v) for k, v in r["job"].items()}} for r in rejected_jobs], indent=2), 
            encoding="utf-8"
        )

        
        self.out_file.parent.mkdir(parents=True, exist_ok=True)
        self.out_file.write_text(json.dumps(out_data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        logging.info(f"Saved to {self.out_file}")
        
if __name__ == "__main__":
    pipeline = InternshipScannerPipeline(Path(__file__).resolve().parent)
    pipeline.run()
