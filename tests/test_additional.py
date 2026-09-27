import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from schema import validate_job_schema, JobRecord
from eligibility import determine_eligibility, EligibilityStatus
from scan import InternshipScannerPipeline
import sources

def test_source_failure_isolation(monkeypatch, tmp_path):
    def fetch_source_A(cfg):
        raise Exception("HTTP 500")
    def fetch_source_B(cfg):
        return [{"title": "Software Intern", "company": "B Corp", "location": "Remote", "remote": True, "url": "https://b.com", "posted_at": datetime.now(timezone.utc)}]
    
    monkeypatch.setattr(sources, "SOURCES", {"A": fetch_source_A, "B": fetch_source_B})
    (tmp_path / "job_titles.txt").write_text("Software Intern")
    
    pipeline = InternshipScannerPipeline(tmp_path)
    pipeline.run()
    
    data = json.loads((tmp_path / "docs" / "data" / "jobs.json").read_text(encoding="utf-8"))
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["company"] == "B Corp"

def test_eligibility_thorough():
    # Must ACCEPT
    assert determine_eligibility("Software Engineering Intern", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Data Science Intern", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Machine Learning Intern", "") == EligibilityStatus.ELIGIBLE
    
    # Must REJECT
    assert determine_eligibility("Senior Software Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Software Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Engineering Manager", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Director of Engineering", "") == EligibilityStatus.NON_INTERNSHIP
    
    # Must carefully evaluate
    assert determine_eligibility("Graduate Software Engineer", "") == EligibilityStatus.UNCERTAIN
    assert determine_eligibility("Student Software Developer", "") == EligibilityStatus.UNCERTAIN
    assert determine_eligibility("Co-op Software Engineer", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Software Engineering Apprentice", "") == EligibilityStatus.UNCERTAIN

def test_deduplication_thorough():
    pipeline = InternshipScannerPipeline(".")
    
    # 1. Same job twice from same source
    j1 = {"title": "A", "company": "B", "location": "C", "url": "http://D"}
    j2 = {"title": "A", "company": "B", "location": "C", "url": "http://D"}
    assert pipeline.fingerprint(j1) == pipeline.fingerprint(j2)
    
    # 2. Same job through two different sources (fingerprint depends on core info, not source)
    j3 = {"title": "A", "company": "B", "location": "C", "url": "http://D", "source": "X"}
    j4 = {"title": "A", "company": "B", "location": "C", "url": "http://D", "source": "Y"}
    assert pipeline.fingerprint(j3) == pipeline.fingerprint(j4)
    
    # 3. Similar titles but different jobs (e.g. Frontend vs Backend)
    j5 = {"title": "Frontend Intern", "company": "B", "location": "C", "url": "http://D"}
    j6 = {"title": "Backend Intern", "company": "B", "location": "C", "url": "http://D"}
    assert pipeline.fingerprint(j5) != pipeline.fingerprint(j6)
    
    # 4. Same company/title but different location
    j7 = {"title": "A", "company": "B", "location": "NY", "url": "http://D"}
    j8 = {"title": "A", "company": "B", "location": "SF", "url": "http://D"}
    assert pipeline.fingerprint(j7) != pipeline.fingerprint(j8)
    
    # 5. Same title/company/location but different URLs
    j9 = {"title": "A", "company": "B", "location": "C", "url": "http://d1"}
    j10 = {"title": "A", "company": "B", "location": "C", "url": "http://d2"}
    assert pipeline.fingerprint(j9) != pipeline.fingerprint(j10)
