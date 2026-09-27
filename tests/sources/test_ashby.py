import pytest
from datetime import datetime, timezone
from sources.adapters.ashby import AshbySource
import sources.adapters.ashby as ashby_module
from scan import InternshipScannerPipeline

def test_ashby_successful_fetch(monkeypatch):
    def mock_get(url, headers=None, max_retries=0, timeout=0):
        if "notion" in url:
            return {
                "jobs": [
                    {
                        "id": "1",
                        "title": "Software Engineering Intern",
                        "jobUrl": "https://jobs.ashbyhq.com/notion/1",
                        "location": "San Francisco",
                        "isRemote": False,
                        "employmentType": "Intern",
                        "publishedAt": "2030-01-01T00:00:00.000Z",
                        "descriptionPlain": "We are looking for interns."
                    },
                    {
                        "id": "2",
                        "title": "Senior Engineer",
                        "jobUrl": "https://jobs.ashbyhq.com/notion/2",
                        "location": "Remote",
                        "isRemote": True,
                        "employmentType": "Full Time",
                        "publishedAt": "2030-01-01T00:00:00.000Z",
                        "descriptionPlain": "Senior role."
                    }
                ]
            }
        return {"jobs": []}
        
    monkeypatch.setattr(ashby_module, "fetch_json", mock_get)
    monkeypatch.setattr(ashby_module, "_companies", lambda k: ["notion", "empty_board"])
    
    adapter = AshbySource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 2
    assert jobs[0]["title"] == "Software Engineering Intern"
    assert jobs[0]["company"] == "Notion"
    assert jobs[0]["remote"] is False
    assert jobs[0]["employment_type"] == "Intern"
    assert jobs[0]["description"] == "We are looking for interns."
    
    assert jobs[1]["title"] == "Senior Engineer"
    assert jobs[1]["remote"] is True
    assert jobs[1]["employment_type"] == "Full Time"

def test_ashby_malformed_and_stale(monkeypatch):
    def mock_get(url, headers=None, max_retries=0, timeout=0):
        return {
            "jobs": [
                {
                    # Stale job
                    "id": "1",
                    "title": "Stale Intern",
                    "jobUrl": "https://jobs.ashbyhq.com/notion/1",
                    "publishedAt": "2020-01-01T00:00:00.000Z",
                },
                {
                    # Malformed date
                    "id": "2",
                    "title": "Malformed Date Intern",
                    "jobUrl": "https://jobs.ashbyhq.com/notion/2",
                    "publishedAt": "not a date",
                },
                {
                    # Missing URL (handled by pipeline schema later, but adapter shouldn't crash)
                    "id": "3",
                    "title": "Missing URL Intern",
                    "publishedAt": "2030-01-01T00:00:00.000Z",
                }
            ]
        }
    monkeypatch.setattr(ashby_module, "fetch_json", mock_get)
    monkeypatch.setattr(ashby_module, "_companies", lambda k: ["test"])
    
    adapter = AshbySource({"global": {"store_max_age_hours": 720}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 2
    assert jobs[0]["title"] == "Stale Intern"
    assert jobs[1]["title"] == "Missing URL Intern"

def test_ashby_http_failure_isolation(monkeypatch):
    def mock_get(url, headers=None, max_retries=0, timeout=0):
        if "bad_board" in url:
            raise Exception("500 Internal Server Error")
        return {"jobs": [{"title": "Good Intern", "publishedAt": "2030-01-01T00:00:00Z"}]}
        
    monkeypatch.setattr(ashby_module, "fetch_json", mock_get)
    monkeypatch.setattr(ashby_module, "_companies", lambda k: ["bad_board", "good_board"])
    
    adapter = AshbySource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    # Should isolate failure and return good board's jobs
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Good Intern"

def test_ashby_empty_response(monkeypatch):
    def mock_get(url, headers=None, max_retries=0, timeout=0):
        return {} # No 'jobs' key
        
    monkeypatch.setattr(ashby_module, "fetch_json", mock_get)
    monkeypatch.setattr(ashby_module, "_companies", lambda k: ["test"])
    
    adapter = AshbySource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 0
