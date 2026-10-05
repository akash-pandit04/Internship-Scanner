import pytest
from sources.adapters.personio import PersonioSource
import sources.adapters.personio as personio_module

def test_personio_successful_fetch(monkeypatch):
    def mock_get(url, headers=None, timeout=10):
        class MockResponse:
            status_code = 200
            content = b"""<?xml version="1.0" encoding="UTF-8"?>
            <workzag-jobs>
                <position>
                    <id>123</id>
                    <name>Software Engineering Intern</name>
                    <office>Berlin, Remote</office>
                    <createdAt>2030-01-01T00:00:00Z</createdAt>
                    <jobDescriptions>
                        <jobDescription>
                            <name>Description</name>
                            <value>Build great software</value>
                        </jobDescription>
                    </jobDescriptions>
                </position>
            </workzag-jobs>"""
        return MockResponse()

    monkeypatch.setattr(personio_module.requests, "get", mock_get)
    monkeypatch.setattr(personio_module, "_companies", lambda: [{"id": "test_board", "name": "Test Co"}])

    adapter = PersonioSource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Engineering Intern"
    assert jobs[0]["company"] == "Test Co"
    assert jobs[0]["location"] == "Berlin, Remote"
    assert "remote" in jobs[0]["location"].lower() or jobs[0]["remote"]
    assert jobs[0]["url"] == "https://test_board.jobs.personio.de/job/123"

def test_personio_http_failure_isolation(monkeypatch):
    def mock_get(url, headers=None, timeout=10):
        if "bad_board" in url:
            raise Exception("500 Internal Server Error")
        
        class MockResponse:
            status_code = 200
            content = b"""<?xml version="1.0" encoding="UTF-8"?>
            <workzag-jobs>
                <position>
                    <id>456</id>
                    <name>Good Intern</name>
                    <createdAt>2030-01-01T00:00:00Z</createdAt>
                </position>
            </workzag-jobs>"""
        return MockResponse()

    monkeypatch.setattr(personio_module.requests, "get", mock_get)
    monkeypatch.setattr(personio_module, "_companies", lambda: [
        {"id": "bad_board", "name": "Bad Co"}, 
        {"id": "good_board", "name": "Good Co"}
    ])

    adapter = PersonioSource({"global": {"store_max_age_hours": 999999}})
    jobs = adapter.fetch()
    
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Good Intern"
    assert jobs[0]["company"] == "Good Co"
