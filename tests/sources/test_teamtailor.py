import pytest
from sources.adapters.teamtailor import TeamtailorSource

@pytest.fixture
def adapter():
    return TeamtailorSource({})

def test_teamtailor_fetch(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.teamtailor._companies", lambda: [{"id": "test", "name": "Test"}])
    
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "items": [
                    {
                        "id": "1",
                        "title": "Backend Intern",
                        "url": "https://test/jobs/1",
                        "date_published": "2026-09-01T00:00:00Z"
                    }
                ]
            }
            
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    
    jobs = adapter.fetch()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Backend Intern"

def test_teamtailor_full_domain(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.teamtailor._companies", lambda: [{"id": "careers.test.com"}])
    
    class MockResponse:
        status_code = 200
        def json(self): return {"items": []}
            
    monkeypatch.setattr("requests.get", lambda url, **k: MockResponse() if "careers.test.com/jobs.json" in url else None)
    adapter.fetch()
