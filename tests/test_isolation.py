def test_failure_isolation_comprehensive(monkeypatch, tmp_path):
    import sources
    from scan import InternshipScannerPipeline
    import json
    
    def fetch_404(cfg): raise Exception("404 Not Found")
    def fetch_429(cfg): raise Exception("429 Too Many Requests")
    def fetch_500(cfg): raise Exception("500 Internal Server Error")
    def fetch_timeout(cfg): raise Exception("Timeout")
    def fetch_malformed(cfg): return "This is not a list"
    
    def fetch_success(cfg):
        from datetime import datetime, timezone
        return [{"title": "A Intern", "company": "B Corp", "location": "Remote", "remote": True, "url": "https://b.com/j", "posted_at": datetime.now(timezone.utc)}]
    
    monkeypatch.setattr(sources, "SOURCES", {
        "s404": fetch_404,
        "s429": fetch_429,
        "s500": fetch_500,
        "stout": fetch_timeout,
        "smal": fetch_malformed,
        "good": fetch_success
    })
    (tmp_path / "job_titles.txt").write_text("A Intern")
    
    pipeline = InternshipScannerPipeline(tmp_path)
    pipeline.run()
    
    data = json.loads((tmp_path / "docs" / "data" / "jobs.json").read_text(encoding="utf-8"))
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["company"] == "B Corp"
