import pytest
from sources.adapters.recruitee import RecruiteeSource

@pytest.fixture
def adapter():
    return RecruiteeSource({})

def test_recruitee_fetch(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.recruitee._companies", lambda: [{"id": "test", "name": "Test"}])
    
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "offers": [
                    {
                        "id": 1,
                        "title": "Data Intern",
                        "location": "NY",
                        "published_at": "2026-09-01T00:00:00Z",
                        "remote": True,
                        "careers_url": "https://test"
                    }
                ]
            }
            
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    
    jobs = adapter.fetch()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Data Intern"
    assert jobs[0]["remote"] is True

def test_recruitee_error(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.recruitee._companies", lambda: [{"id": "test"}])
    monkeypatch.setattr("requests.get", lambda *a, **k: 1/0)
    assert adapter.fetch() == []
