import pytest
from sources.adapters.eures import EuresSource

@pytest.fixture
def adapter():
    return EuresSource({})

def test_eures_fetch_missing_creds(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.eures._config", lambda: {})
    assert adapter.fetch() == []

def test_eures_fetch(monkeypatch, adapter):
    monkeypatch.setattr("sources.adapters.eures._config", lambda: {"client_id": "test", "client_secret": "test"})
    # Since it's unimplemented actual fetch, it returns []
    assert adapter.fetch() == []
