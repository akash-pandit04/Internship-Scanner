import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from schema import validate_job_schema, JobRecord
from eligibility import determine_eligibility, EligibilityStatus
from scan import InternshipScannerPipeline

def test_schema_valid_record():
    valid = {
        "title": "Software Engineer Intern",
        "company": "Tech Corp",
        "location": "Remote",
        "remote": True,
        "url": "https://real-company.com/job",
        "source": "test_source",
        "posted_at": datetime.now(timezone.utc)
    }
    assert validate_job_schema(valid) is True

def test_schema_missing_fields():
    invalid = {
        "title": "Software Engineer Intern",
        # missing company
        "location": "Remote",
        "remote": True,
        "url": "https://real-company.com/job",
        "source": "test_source",
        "posted_at": datetime.now(timezone.utc)
    }
    assert validate_job_schema(invalid) is False

def test_schema_invalid_url():
    invalid = {
        "title": "Software Engineer Intern",
        "company": "Tech Corp",
        "location": "Remote",
        "remote": True,
        "url": "not-a-url",
        "source": "test_source",
        "posted_at": datetime.now(timezone.utc)
    }
    assert validate_job_schema(invalid) is False

def test_eligibility_valid_internship():
    assert determine_eligibility("Software Engineering Intern", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Data Science Co-op", "") == EligibilityStatus.ELIGIBLE

def test_eligibility_obvious_full_time():
    assert determine_eligibility("Senior Software Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Director of Engineering", "") == EligibilityStatus.NON_INTERNSHIP

def test_eligibility_uncertain_student_role():
    assert determine_eligibility("Student Ambassador", "Promote our brand") == EligibilityStatus.UNCERTAIN

def test_eligibility_hidden_internship():
    # 'internship' in description but not in title
    assert determine_eligibility("Summer Technical Program", "This is an internship.") == EligibilityStatus.UNCERTAIN

def test_deduplication():
    pipeline = InternshipScannerPipeline(".")
    job1 = {"company": "A", "title": "B", "location": "C", "url": "http://D"}
    job2 = {"company": "A", "title": "B", "location": "C", "url": "http://D"}
    job3 = {"company": "X", "title": "B", "location": "C", "url": "http://D"}
    
    fp1 = pipeline.fingerprint(job1)
    fp2 = pipeline.fingerprint(job2)
    fp3 = pipeline.fingerprint(job3)
    
    assert fp1 == fp2
    assert fp1 != fp3

def test_pipeline_integration(monkeypatch, tmp_path):
    from sources.registry import SourceRegistry
    from sources.base import BaseSource
    class MockAdapter(BaseSource):
        def fetch(self):
            return [
                {
                    "title": "Software Intern",
                    "company": "Valid Corp",
                    "location": "Remote",
                    "remote": True,
                    "url": "https://valid.com",
                    "posted_at": datetime.now(timezone.utc)
                },
                {
                    "title": "Senior Engineer", # Should be rejected by eligibility
                    "company": "Invalid Corp",
                    "location": "Remote",
                    "remote": True,
                    "url": "https://invalid.com",
                    "posted_at": datetime.now(timezone.utc)
                },
                {
                    # Missing URL, should be rejected by schema
                    "title": "Data Intern",
                    "company": "Missing URL Corp",
                    "location": "Remote",
                    "remote": True,
                    "posted_at": datetime.now(timezone.utc)
                }
            ]
    monkeypatch.setattr(SourceRegistry, "get_sources", lambda cfg: {"mock": MockAdapter(cfg)})
    
    (tmp_path / "job_titles.txt").write_text("Software Intern")
    
    pipeline = InternshipScannerPipeline(tmp_path)
    pipeline.run()
    
    out_file = tmp_path / "docs" / "data" / "jobs.json"
    assert out_file.exists()
    
    data = json.loads(out_file.read_text(encoding="utf-8"))
    jobs = data["jobs"]
    
    assert len(jobs) == 1
    assert jobs[0]["company"] == "Valid Corp"
