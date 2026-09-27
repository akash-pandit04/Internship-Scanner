def test_greenhouse_partial_failure(monkeypatch, tmp_path):
    from scan import InternshipScannerPipeline
    import sources
    import json
    from datetime import datetime, timezone

    def mock_get(url):
        class MockResponse:
            def __init__(self, url):
                self.url = url
            def json(self):
                if "fail_company" in self.url:
                    raise Exception("404 Not Found")
                if "jobs/" in self.url:
                    return {"content": "Detail content"}
                return {"jobs": [{"id": "1", "title": "A Intern", "location": {"name": "Remote"}, "absolute_url": "http://url", "updated_at": "2023-01-01T00:00:00+00:00"}]}
        return MockResponse(url)

    monkeypatch.setattr(sources, "get", mock_get)
    
    pipeline = InternshipScannerPipeline(tmp_path)
    pipeline.config = {"store_max_age_hours": 999999}
    
    def mock_companies(kind):
        if kind == "greenhouse":
            return ["good_company", "fail_company"]
        return []
    monkeypatch.setattr(sources, "_companies", mock_companies)
    
    res = sources.fetch_greenhouse(pipeline.config)
    
    assert len(res) == 1
    assert res[0]["company"] == "Good_Company"
