def test_failure_isolation_comprehensive(monkeypatch, tmp_path):
    from sources.registry import SourceRegistry
    from sources.base import BaseSource
    from scan import InternshipScannerPipeline
    import json
    
    class Mock404(BaseSource):
        def fetch(self): raise Exception("404 Not Found")
    class Mock429(BaseSource):
        def fetch(self): raise Exception("429 Too Many Requests")
    class Mock500(BaseSource):
        def fetch(self): raise Exception("500 Internal Server Error")
    class MockTimeout(BaseSource):
        def fetch(self): raise Exception("Timeout")
    class MockMalformed(BaseSource):
        def fetch(self): return "This is not a list"
    class MockSuccess(BaseSource):
        def fetch(self):
            from datetime import datetime, timezone
            return [{"title": "A Intern", "company": "B Corp", "location": "Remote", "remote": True, "url": "https://b.com/j", "posted_at": datetime.now(timezone.utc)}]

    monkeypatch.setattr(SourceRegistry, "get_sources", lambda cfg: {
        "s404": Mock404(cfg),
        "s429": Mock429(cfg),
        "s500": Mock500(cfg),
        "stout": MockTimeout(cfg),
        "smal": MockMalformed(cfg),
        "good": MockSuccess(cfg)
    })
    (tmp_path / "job_titles.txt").write_text("A Intern")
    
    pipeline = InternshipScannerPipeline(tmp_path)
    pipeline.run()
    
    data = json.loads((tmp_path / "docs" / "data" / "jobs.json").read_text(encoding="utf-8"))
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["company"] == "B Corp"
