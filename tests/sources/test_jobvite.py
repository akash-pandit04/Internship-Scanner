import pytest
from sources.adapters.jobvite import JobviteSource

@pytest.fixture
def adapter():
    return JobviteSource({})

def test_jobvite_fetch(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.jobvite._companies", lambda: [{"company_id": "test"}])
    
    class MockResponse:
        status_code = 200
        text = "<xml></xml>"
        content = b"""
        <result>
            <job>
                <id>1</id>
                <title>QA Intern</title>
                <detail-url>https://jobvite</detail-url>
                <date>2026-09-01</date>
                <location>Remote</location>
            </job>
        </result>
        """
            
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    
    jobs = adapter.fetch()
    assert len(jobs) == 1
    assert jobs[0]["title"] == "QA Intern"
    assert jobs[0]["remote"] is True

def test_jobvite_html_redirect(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.jobvite._companies", lambda: [{"company_id": "test"}])
    
    class MockResponse:
        status_code = 200
        text = "<!DOCTYPE html><html>"
            
    monkeypatch.setattr("requests.get", lambda *a, **k: MockResponse())
    
    assert adapter.fetch() == []
