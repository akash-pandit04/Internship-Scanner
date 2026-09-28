def test_greenhouse_partial_failure(monkeypatch, tmp_path):
    from scan import InternshipScannerPipeline
    from sources.adapters.legacy import GreenhouseSource
    import sources.adapters.legacy as l_sources
    import json
    from datetime import datetime, timezone

    def mock_get(url, headers=None, max_retries=0, timeout=0):
        if "fail_company" in url:
            raise Exception("404 Not Found")
        if "jobs/" in url:
            return {"content": "Detail content"}
        return {"jobs": [{"id": "1", "title": "A Intern", "location": {"name": "Remote"}, "absolute_url": "http://url", "updated_at": "2023-01-01T00:00:00+00:00"}]}

    monkeypatch.setattr(l_sources, "fetch_json", mock_get)
    
    pipeline = InternshipScannerPipeline(tmp_path)
    pipeline.config = {"store_max_age_hours": 999999}
    
    def mock_companies(kind):
        if kind == "greenhouse":
            return [{"id": "good_company"}, {"id": "fail_company"}]
        return []
    monkeypatch.setattr(l_sources, "_companies", mock_companies)
    
    adapter = GreenhouseSource({"global": pipeline.config})
    res = adapter.fetch()
    
    assert len(res) == 1
    assert res[0]["company"] == "Good_Company"
