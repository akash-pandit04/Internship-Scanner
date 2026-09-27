import json
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

import scoring
from sources.registry import SourceRegistry

# Make sure adapters are registered
import sources.adapters.legacy
import sources.adapters.ashby
import sources.adapters.smartrecruiters
from eligibility import determine_eligibility, EligibilityStatus
from schema import validate_job_schema, JobRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class TaxonomyRule:
    def __init__(self, category: str, title_patterns: List[str], exclude_title: List[str] = None, desc_patterns: List[str] = None):
        self.category = category
        
        def make_regex(p):
            # If pattern ends with a non-word char (like '.'), standard \b fails if followed by space.
            # We can use (?!\w) instead of \b at the end, and (?<!\w) instead of \b at the start.
            return re.compile(r'(?<!\w)' + p + r'(?!\w)', re.IGNORECASE)

        self.title_patterns = [make_regex(p) for p in title_patterns]
        self.exclude_title = [make_regex(p) for p in (exclude_title or [])]
        self.desc_patterns = [make_regex(p) for p in (desc_patterns or [])]

    def match(self, title: str, description: str) -> bool:
        title_lower = title.lower()
        desc_lower = description.lower()
        
        for ex in self.exclude_title:
            if ex.search(title_lower):
                return False
                
        for p in self.title_patterns:
            if p.search(title_lower):
                return True
                
        for dp in self.desc_patterns:
            if dp.search(desc_lower):
                return True
                
        return False

class JobCategorizer:
    def __init__(self):
        self.rules = [
            TaxonomyRule("Software Engineering", 
                title_patterns=["software engineer", "software engineering", "software developer", "swe", "sde", "software application", "software intern", "software development"],
                exclude_title=["vp", "director", "sales", "hr", "manager", "people ops"],
                desc_patterns=["software engineering intern", "software developer intern"]
            ),
            TaxonomyRule("Backend Development", 
                title_patterns=["backend", "back-end", "back end", "server-side", "api developer"]
            ),
            TaxonomyRule("Frontend Development", 
                title_patterns=["frontend", "front-end", "front end", "client-side", "ui developer", "web developer", "web development"]
            ),
            TaxonomyRule("Full-Stack Development", 
                title_patterns=["fullstack", "full-stack", "full stack"]
            ),
            TaxonomyRule("Mobile Development", 
                title_patterns=["mobile developer", "ios", "android", "react native", "flutter", "mobile application"]
            ),
            TaxonomyRule("Data Science", 
                title_patterns=["data scientist", "data science", "applied scientist", "research scientist"]
            ),
            TaxonomyRule("Data Analytics", 
                title_patterns=["data analyst", "data analytics", "business intelligence", "bi analyst", "product analyst", "quantitative analyst", "quant intern"],
                exclude_title=["data entry", "hr", "sales"]
            ),
            TaxonomyRule("Data Engineering", 
                title_patterns=["data engineer", "data engineering", "big data", "data pipeline"]
            ),
            TaxonomyRule("AI / Machine Learning", 
                title_patterns=["ai", r"a\.i\.", "machine learning", "ml", "deep learning", "artificial intelligence", "vla", "vision-language"]
            ),
            TaxonomyRule("NLP", 
                title_patterns=["nlp", "natural language processing", "llm", "language model", "computational linguistics"]
            ),
            TaxonomyRule("Computer Vision", 
                title_patterns=["computer vision", "vision", "cv", "image processing", "video processing"]
            ),
            TaxonomyRule("Cloud Computing", 
                title_patterns=["cloud computing", "cloud engineer", "aws engineer", "azure engineer", "gcp engineer", "cloud software", "cloud intern"],
                desc_patterns=["cloud engineering intern"]
            ),
            TaxonomyRule("DevOps", 
                title_patterns=["devops", "dev ops", "ci/cd", "infrastructure", "release engineer"]
            ),
            TaxonomyRule("SRE", 
                title_patterns=["sre", "site reliability", "reliability engineer"]
            ),
            TaxonomyRule("Cybersecurity", 
                title_patterns=["security", "cybersecurity", "cyber", "infosec", "information security", "penetration", "appsec"]
            ),
            TaxonomyRule("QA / Testing", 
                title_patterns=["qa", "quality assurance", "test engineer", "tester", "software testing", "sdet"]
            ),
            TaxonomyRule("Automation", 
                title_patterns=["automation engineer", "test automation"]
            ),
            TaxonomyRule("Database Engineering", 
                title_patterns=["database", "dba", "sql developer", "data architect"]
            ),
            TaxonomyRule("Systems Engineering", 
                title_patterns=["systems engineer", "systems engineering", "operating systems", "robotics"]
            ),
            TaxonomyRule("Embedded Systems", 
                title_patterns=["embedded", "embedded software", "embedded systems", "microcontroller"]
            ),
            TaxonomyRule("Firmware", 
                title_patterns=["firmware"]
            ),
            TaxonomyRule("Networking", 
                title_patterns=["network", "networking", "wireless", "telecom"]
            ),
            TaxonomyRule("Blockchain/Web3", 
                title_patterns=["blockchain", "web3", "crypto", "smart contract"]
            ),
            TaxonomyRule("AR/VR", 
                title_patterns=["ar", "vr", "xr", "augmented reality", "virtual reality", "mixed reality"]
            ),
            TaxonomyRule("Game Development", 
                title_patterns=["game", "gaming", "unreal", "unity", "gameplay"]
            ),
            TaxonomyRule("Research", 
                title_patterns=["research", "researcher", "research assistant", "r&d"],
                exclude_title=["user research", "ux research"]
            ),
            TaxonomyRule("Technical Product", 
                title_patterns=["product manager", "product management", "tpm", "technical product"],
                exclude_title=["product marketing", "product designer"]
            ),
            TaxonomyRule("UI/UX for Software", 
                title_patterns=["ui/ux", "ux/ui", "product design", "product designer", "user experience", "user interface", "ux research"],
                exclude_title=["graphic design", "visual design", "marketing design"]
            )
        ]

    def categorize(self, title: str, description: str) -> List[str]:
        cats = []
        for rule in self.rules:
            if rule.match(title, description):
                cats.append(rule.category)
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

    def fetch_source(self, name: str, adapter) -> List[Dict[str, Any]]:
        logging.info(f"Fetching from {name}...")
        try:
            raws = adapter.fetch()
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
        
        adapters = SourceRegistry.get_sources(self.config)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for name, adapter in adapters.items():
                futures.append(executor.submit(self.fetch_source, name, adapter))
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
            eligibility = determine_eligibility(raw.get("title", ""), raw.get("description", ""), raw.get("employment_type", ""))
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
