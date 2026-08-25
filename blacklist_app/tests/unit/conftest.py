import pytest

@pytest.fixture(autouse=True)
def bearer_token_env(monkeypatch):
    monkeypatch.setenv("BEARER_TOKEN", "bearer_token_test")
