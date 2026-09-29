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
import sources.adapters.ycombinator
import sources.adapters.themuse
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
        location = str(job.get("location", "")).strip().lower()
        url = str(job.get("url", "")).strip().lower()
        
        raw_fp = f"{company}|{title}|{location}|{url}"
        import hashlib
        return hashlib.md5(raw_fp.encode('utf-8')).hexdigest()[:12]
        
    def is_retained(self, raw_job: dict, now: datetime) -> bool:
        retention_days = self.config.get("global", {}).get("retention_days", 30)
        posted_at = raw_job.get("posted_at")
        if not posted_at:
            return True # missing dates are accepted
        try:
            age = now - posted_at
            return age.total_seconds() <= (retention_days * 86400)
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
        
        import json
        reg_file = self.root / "docs" / "data" / "registry_metrics.json"
        reg_metrics = {}
        if reg_file.exists():
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    reg_metrics = json.load(f)
            except: pass

        
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
                    
            for adapter in adapters.values():
                if hasattr(adapter, 'employer_stats'):
                    for emp, stats in adapter.employer_stats.items():
                        if emp not in reg_metrics:
                            reg_metrics[emp] = {"scans_attempted": 0, "successful_scans": 0, "raw_jobs": 0, "fresh_jobs": 0, "internship_jobs": 0, "cse_jobs": 0, "exact_duplicates": 0, "semantic_duplicates": 0, "ambiguous_duplicates": 0, "new_cse_jobs": 0, "last_successful_scan": None, "last_cse_job_seen": None, "last_new_cse_job_seen": None, "status": "UNKNOWN"}
                        reg_metrics[emp]["scans_attempted"] += 1
                        reg_metrics[emp]["status"] = stats.get("status", "UNKNOWN")
                        if stats.get("status") == "HEALTHY":
                            reg_metrics[emp]["successful_scans"] += 1
                            reg_metrics[emp]["last_successful_scan"] = now.isoformat()

                
        logging.info(f"Fetched {len(raw_jobs)} raw records across all sources.")
        
        processed_jobs: Dict[str, JobRecord] = {}
        rejected_jobs = []
        metrics = {
            "fetched": len(raw_jobs),
            "normalized": 0,
            "schema_rejected": 0,
            "expired_rejected": 0,
            "non_internship": 0,
            "uncertain": 0,
            "accepted": 0,
            "exact_duplicates": 0,
            "semantic_duplicates": 0,
            "ambiguous_duplicates": 0
        }
        
        for raw in raw_jobs:
            emp = raw.get("employer_id") or (raw.get("source") if raw.get("source") not in ["greenhouse", "lever", "ashby", "smartrecruiters"] else None)
            if emp and emp not in reg_metrics:
                reg_metrics[emp] = {"scans_attempted": 1, "successful_scans": 1, "raw_jobs": 0, "fresh_jobs": 0, "internship_jobs": 0, "cse_jobs": 0, "exact_duplicates": 0, "semantic_duplicates": 0, "ambiguous_duplicates": 0, "new_cse_jobs": 0, "last_successful_scan": now.isoformat(), "last_cse_job_seen": None, "last_new_cse_job_seen": None, "status": "HEALTHY"}
            
            if emp: reg_metrics[emp]["raw_jobs"] += 1

            # 1. Normalize
            if "description" not in raw:
                raw["description"] = ""
            if "employment_type" not in raw:
                raw["employment_type"] = ""
            metrics["normalized"] += 1
                

            title_lower = str(raw.get("title", "")).lower()
            reject_keywords = ["(m/w/d)", "(f/m/d)", "werkstudent", "praktikant", "gyakornok", 
                               "développeur", "ingénieur", "alternance", "stagaire", "stage", 
                               "managerin", "creatorin", "mensch"]
            if any(k in title_lower for k in reject_keywords):
                metrics["schema_rejected"] += 1
                rejected_jobs.append({"reason": "non_english", "job": raw})
                continue
            
            try:
                from langdetect import detect, DetectorFactory
                DetectorFactory.seed = 0
                text_to_detect = str(raw.get("title", "")) + ". " + str(raw.get("company", ""))
                lang = detect(text_to_detect)
                if lang not in ['en']:
                    if not any(k in title_lower for k in ["engineer", "developer", "analyst", "intern"]):
                        metrics["schema_rejected"] += 1
                        rejected_jobs.append({"reason": "non_english", "job": raw})
                        continue
            except Exception:
                pass
            
            # 2. Schema Validation

            if not validate_job_schema(raw):
                metrics["schema_rejected"] += 1
                rejected_jobs.append({"reason": "schema", "job": raw})
                continue
                
            # 2.5 Retention Filtering
            if not self.is_retained(raw, now):
                metrics["expired_rejected"] += 1
                rejected_jobs.append({"reason": "expired", "job": raw})
                continue
            if emp: reg_metrics[emp]["fresh_jobs"] += 1
                
            # 3. Eligibility
            eligibility = determine_eligibility(raw.get("title", ""), raw.get("description", ""), raw.get("employment_type", ""))
            if eligibility == EligibilityStatus.ELIGIBLE:
                raw["job_type"] = "internship"
                if emp: reg_metrics[emp]["internship_jobs"] += 1
            else:
                raw["job_type"] = "job"
                if eligibility == EligibilityStatus.NON_INTERNSHIP:
                    metrics["non_internship"] += 1
                else:
                    metrics["uncertain"] += 1
                
            # 4. Categorization
            cats = self.categorizer.categorize(raw["title"], raw["description"])
            if cats and emp:
                reg_metrics[emp]["cse_jobs"] += 1
                reg_metrics[emp]["last_cse_job_seen"] = now.isoformat()
            
            # 5. Scoring
            score_data = scoring.score_job(raw, self.config)
            
            # 6. Deduplication
            fp = self.fingerprint(raw)
            url = str(raw.get("url", "")).strip().lower()
            source = str(raw.get("source", ""))
            job_id = str(raw.get("id", ""))
            
            c_norm = re.sub(r'(inc|llc|corp|corporation|ltd|limited|co|company)', '', str(raw.get("company", "")).lower())
            c_norm = re.sub(r'[^a-z0-9]', '', c_norm)
            
            t_norm = re.sub(r'(internship|intern|co-op|student)', '', str(raw.get("title", "")).lower())
            t_norm = re.sub(r'[^a-z0-9]', '', t_norm)
            
            dup_reason = None
            if fp in processed_jobs:
                dup_reason = "exact_duplicates"
            else:
                for exist_fp, exist_job in processed_jobs.items():
                    e_url = str(exist_job.url).strip().lower()
                    if url and url == e_url:
                        dup_reason = "exact_duplicates"
                        break
                    if source == exist_job.source and job_id == str(exist_job.id):
                        dup_reason = "exact_duplicates"
                        break
                        
                    e_c = re.sub(r'(inc|llc|corp|corporation|ltd|limited|co|company)', '', str(exist_job.company).lower())
                    e_c = re.sub(r'[^a-z0-9]', '', e_c)
                    if c_norm and e_c and c_norm == e_c:
                        # Same company, check title and location
                        e_loc = re.sub(r'[^a-z0-9]', '', str(exist_job.location).lower())
                        c_loc = re.sub(r'[^a-z0-9]', '', str(raw.get("location", "")).lower())
                        
                        loc_match = False
                        if not c_loc or not e_loc:
                            loc_match = True
                        elif c_loc in e_loc or e_loc in c_loc:
                            loc_match = True
                        
                        if not loc_match:
                            continue
                            
                        e_t = re.sub(r'(internship|intern|co-op|student)', '', str(exist_job.title).lower())
                        e_t = re.sub(r'[^a-z0-9]', '', e_t)
                        if t_norm == e_t:
                            dup_reason = "semantic_duplicates"
                            break
                        import difflib
                        ratio = difflib.SequenceMatcher(None, t_norm, e_t).ratio()
                        if ratio > 0.8:
                            dup_reason = "semantic_duplicates"
                            break
                        elif ratio > 0.6:
                            dup_reason = "ambiguous_duplicates"
                            
            if dup_reason:
                metrics[dup_reason] += 1
                rejected_jobs.append({"reason": dup_reason, "job": raw})
                if emp and dup_reason in reg_metrics[emp]:
                    reg_metrics[emp][dup_reason] += 1
                continue
                
            if cats and emp:
                reg_metrics[emp]["new_cse_jobs"] += 1
                reg_metrics[emp]["last_new_cse_job_seen"] = now.isoformat()

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
                score=score_data["score"],
                job_type=raw.get("job_type", "internship")
            )
            processed_jobs[fp] = record
            metrics["accepted"] += 1
            
        logging.info(f"Metrics: {metrics}")
        logging.info(f"Pipeline complete. Yielded {len(processed_jobs)} valid unique internships.")
        
        # Save registry metrics
        reg_file.parent.mkdir(parents=True, exist_ok=True)
        reg_file.write_text(json.dumps(reg_metrics, ensure_ascii=False, indent=2), encoding="utf-8")

        
        # Save output
        companies_path = self.root / "companies.json"
        total_endpoints = 0
        if companies_path.exists():
            import json
            comps = json.loads(companies_path.read_text(encoding="utf-8"))
            total_endpoints += sum(len(v) if isinstance(v, list) else 1 for v in comps.values())
        total_endpoints += 10 # Add static adapters like legacy

        out_data = {
            "generated_at": now.isoformat(),
            "config": {"retention_days": self.config.get("global", {}).get("retention_days", 30)},
            "all_sources": list(adapters.keys()),
            "total_endpoints": total_endpoints,
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
        # Generate Sitemap
        sitemap_path = self.out_file.parent.parent / "sitemap.xml"
        robots_path = self.out_file.parent.parent / "robots.txt"
        base_url = "https://internshipscanner.com" # Placeholder base URL
        
        url_nodes = []
        import re
        for j in processed_jobs.values():
            slug = re.sub(r'[^a-z0-9]+', '-', f"{j.title}-{j.company}".lower()).strip('-')
            url = f"{base_url}/#!/job/{slug}/{j.id}"
            url_nodes.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{now.strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
  </url>""")
        
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}/</loc>
    <changefreq>hourly</changefreq>
    <priority>1.0</priority>
  </url>
{"".join(url_nodes)}
</urlset>"""
        
        sitemap_path.write_text(sitemap_content, encoding="utf-8")
        
        robots_content = f"""User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml"""
        robots_path.write_text(robots_content, encoding="utf-8")

        
if __name__ == "__main__":
    pipeline = InternshipScannerPipeline(Path(__file__).resolve().parent)
    pipeline.run()
