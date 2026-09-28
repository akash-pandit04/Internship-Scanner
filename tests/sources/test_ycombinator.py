import pytest
from sources.adapters.ycombinator import YCombinatorSource

def test_ycombinator_isolation_429(monkeypatch):
    source = YCombinatorSource({'enabled': True})
    def mock_fetch(*args, **kwargs):
        raise Exception("Simulated 429")
    monkeypatch.setattr('sources.adapters.ycombinator.fetch_text', mock_fetch)
    # Fast roles and locations list to speed up test
    source.ROLES = ['software-engineer']
    source.LOCATIONS = []
    jobs = source.fetch()
    assert len(jobs) == 0

def test_ycombinator_bad_html(monkeypatch):
    source = YCombinatorSource({'enabled': True})
    def mock_fetch(*args, **kwargs):
        return "<html><body>No data-page attribute here!</body></html>"
    monkeypatch.setattr('sources.adapters.ycombinator.fetch_text', mock_fetch)
    source.ROLES = ['software-engineer']
    source.LOCATIONS = []
    jobs = source.fetch()
    assert len(jobs) == 0
