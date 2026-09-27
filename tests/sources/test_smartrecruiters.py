import pytest
from datetime import datetime
from sources.adapters.smartrecruiters import SmartRecruitersSource
import sources.adapters.smartrecruiters as sr_module

def test_smartrecruiters_successful_fetch(monkeypatch):
    def mock_get(url, headers=None, max_retries=0, timeout=0):
        if "offset=0" in url:
            return {
                "offset": 0,
                "limit": 100,
                "totalFound": 101,
                "content": [
                    {
                        "id": "1",
                        "name": "Software Engineering Intern",
                        "company": {"identifier": "canva", "name": "Canva"},
                        "location": {"city": "Sydney", "remote": False},
                        "typeOfEmployment": {"id": "intern", "label": "Intern"},
                        "releasedDate": "2030-01-01T00:00:00.000Z"
                    }
                ]
            }
        elif "offset=100" in url:
            return {
                "offset": 100,
                "limit": 100,
                "totalFound": 101,
                "content": [
                    {
                        "id": "2",
                        "name": "Senior Engineer",
                        "company": {"identifier": "canva", "name": "Canva"},
                        "location": {"city": "Remote", "remote": True},
                        "typeOfEmployment": {"id": "permanent", "label": "Permanent"},
                        "releasedDate": "2030-01-01T00:00:00.000Z"
                    }
                ]
            }
        return {"content": []}
        
    monkeypatch.setattr(sr_module, "fetch_json", mock_get)
    monkeypatch.setattr(sr_module, "_companies", lambda k: ["canva"])
    
    adapter = SmartRecruitersSource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 2
    
    assert jobs[0]["title"] == "Software Engineering Intern"
    assert jobs[0]["company"] == "Canva"
    assert jobs[0]["remote"] is False
    assert jobs[0]["employment_type"] == "Intern"
    assert jobs[0]["url"] == "https://jobs.smartrecruiters.com/canva/1"
    
    assert jobs[1]["title"] == "Senior Engineer"
    assert jobs[1]["remote"] is True
    assert jobs[1]["employment_type"] == "Permanent"

def test_smartrecruiters_http_failure_isolation(monkeypatch):
    def mock_get(url, headers=None, max_retries=0, timeout=0):
        if "bad_board" in url:
            raise Exception("500 Internal Server Error")
        return {"content": [{"name": "Good Intern", "releasedDate": "2030-01-01T00:00:00Z"}]}
        
    monkeypatch.setattr(sr_module, "fetch_json", mock_get)
    monkeypatch.setattr(sr_module, "_companies", lambda k: ["bad_board", "good_board"])
    
    adapter = SmartRecruitersSource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Good Intern"
