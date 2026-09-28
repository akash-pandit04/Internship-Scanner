import sys
from pathlib import Path

path = Path('scan.py')
text = path.read_text(encoding='utf-8')

# 1. Load registry metrics
load_code = """        logging.info("Starting internship scanner pipeline...")
        scoring.load_titles(self.root / self.config.get("job_titles_file", "job_titles.txt"))
        
        reg_file = self.root / "docs" / "data" / "registry_metrics.json"
        reg_metrics = {}
        if reg_file.exists():
            import json
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    reg_metrics = json.load(f)
            except: pass
"""
text = text.replace('        logging.info("Starting internship scanner pipeline...")\n        scoring.load_titles(self.root / self.config.get("job_titles_file", "job_titles.txt"))', load_code)


# 2. Collect adapter stats
collect_code = """        for future in futures:
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
"""
text = text.replace('        for future in futures:\n                res = future.result()\n                if isinstance(res, list):\n                    raw_jobs.extend(res)\n                else:\n                    logging.error(f"Source adapter returned non-list: {type(res)}")', collect_code)


# 3. Track metrics inside the loop
loop_code = """        for raw in raw_jobs:
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
            if emp: reg_metrics[emp]["fresh_jobs"] += 1
                
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
            if emp: reg_metrics[emp]["internship_jobs"] += 1
                
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
            
            c_norm = re.sub(r'\\b(inc|llc|corp|corporation|ltd|limited|co|company)\\b', '', str(raw.get("company", "")).lower())
            c_norm = re.sub(r'[^a-z0-9]', '', c_norm)
            
            t_norm = re.sub(r'\\b(internship|intern|co-op|student)\\b', '', str(raw.get("title", "")).lower())
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
                        
                    e_c = re.sub(r'\\b(inc|llc|corp|corporation|ltd|limited|co|company)\\b', '', str(exist_job.company).lower())
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
                            
                        e_t = re.sub(r'\\b(internship|intern|co-op|student)\\b', '', str(exist_job.title).lower())
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
"""

# I will use a regex to replace the whole `for raw in raw_jobs:` loop block
import re
text = re.sub(r'        for raw in raw_jobs:\n(.*?)            record = JobRecord\(', loop_code + '\n            record = JobRecord(', text, flags=re.DOTALL)

# 4. Save registry metrics
save_code = """        logging.info(f"Pipeline complete. Yielded {len(processed_jobs)} valid unique internships.")
        
        # Save registry metrics
        reg_file.parent.mkdir(parents=True, exist_ok=True)
        reg_file.write_text(json.dumps(reg_metrics, ensure_ascii=False, indent=2), encoding="utf-8")
"""
text = text.replace('        logging.info(f"Pipeline complete. Yielded {len(processed_jobs)} valid unique internships.")', save_code)

path.write_text(text, encoding='utf-8')
print("Patched scan.py")
