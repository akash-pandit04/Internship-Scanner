import pytest
from sources.adapters.workday import WorkdaySource

@pytest.fixture
def adapter():
    return WorkdaySource({})

def test_workday_fetch(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.workday._companies", lambda: [{"host": "wd", "tenant": "t", "report_name": "r"}])
    
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "Report_Entry": [
                    {
                        "title": "Systems Intern",
                        "url": "https://test",
                        "location": "SF",
                        "posted_on": "2026-09-01"
                    }
                ]
            }
            
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    
    jobs = adapter.fetch()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Systems Intern"
