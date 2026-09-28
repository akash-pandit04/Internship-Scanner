import pytest
from sources.adapters.bamboohr import BambooHRSource

@pytest.fixture
def adapter():
    return BambooHRSource({})

def test_bamboohr_fetch(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.bamboohr._companies", lambda: [{"id": "test", "name": "Test Co"}])
    
    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "result": [
                    {
                        "id": "123",
                        "jobOpeningName": "Software Engineering Intern",
                        "location": {"city": "Remote"}
                    }
                ]
            }
            
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    
    jobs = adapter.fetch()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineering Intern"
    assert jobs[0]["company"] == "Test Co"
    assert jobs[0]["remote"] is True

def test_bamboohr_http_error(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.bamboohr._companies", lambda: [{"id": "test"}])
    
    class MockResponse:
        status_code = 500
        
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    assert adapter.fetch() == []
