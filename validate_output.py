import json
import sys
from pathlib import Path
from schema import validate_job_schema
from datetime import datetime

def check_jobs_json():
    jobs_file = Path("docs/data/jobs.json")
    if not jobs_file.exists():
        print("Error: jobs.json does not exist.")
        sys.exit(1)
        
    try:
        data = json.loads(jobs_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        print("Error: jobs.json is not valid JSON.")
        sys.exit(1)
        
    if "jobs" not in data:
        print("Error: 'jobs' key missing from jobs.json.")
        sys.exit(1)
        
    jobs = data["jobs"]
    print(f"Validating {len(jobs)} jobs...")
    
    seen_ids = set()
    seen_urls = set()
    
    from eligibility import determine_eligibility, EligibilityStatus
    
    for job in jobs:
        # Convert strings back to datetime for schema validation
        try:
            if job.get('posted_at'):
                job['posted_at'] = datetime.fromisoformat(job['posted_at'])
            if job.get('fetched_at'):
                job['fetched_at'] = datetime.fromisoformat(job['fetched_at'])
        except Exception as e:
            print(f"Error parsing dates for job {job.get('id')}: {e}")
            sys.exit(1)
            
        if not validate_job_schema(job):
            print(f"Data Quality Error: Invalid schema for job -> {job.get('title')} at {job.get('company')}")
            sys.exit(1)
            
        # Deduplication check
        if job["id"] in seen_ids:
            print(f"Data Quality Error: Duplicate ID found -> {job['id']}")
            sys.exit(1)
        seen_ids.add(job["id"])
        
        if job["url"] in seen_urls:
            print(f"Data Quality Error: Duplicate Application URL found -> {job['url']}")
            sys.exit(1)
        seen_urls.add(job["url"])
        
        # Eligibility check
        elig = determine_eligibility(job.get('title', ''), job.get('description', ''), job.get('employment_type', ''))
        if elig != EligibilityStatus.ELIGIBLE:
            print(f"Data Quality Error: Non-internship job made it to output -> {job.get('title')}")
            sys.exit(1)
            
    print("Success: All jobs passed data quality checks.")
    sys.exit(0)

if __name__ == "__main__":
    check_jobs_json()

