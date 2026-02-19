import importlib

import verdictswarm_mcp.config as config


def test_config_defaults(monkeypatch):
    monkeypatch.delenv("VS_API_URL", raising=False)
    monkeypatch.delenv("VS_API_KEY", raising=False)
    monkeypatch.delenv("VS_TIMEOUT", raising=False)

    cfg = importlib.reload(config)

    assert cfg.VS_API_URL == "https://verdictswarm-production.up.railway.app"
    assert cfg.VS_API_KEY == ""
    assert cfg.VS_TIMEOUT == 120


def test_config_env_overrides(monkeypatch):
    monkeypatch.setenv("VS_API_URL", "https://custom.example.com")
    monkeypatch.setenv("VS_API_KEY", "abc123")
    monkeypatch.setenv("VS_TIMEOUT", "30")

    cfg = importlib.reload(config)

    assert cfg.VS_API_URL == "https://custom.example.com"
    assert cfg.VS_API_KEY == "abc123"
    assert cfg.VS_TIMEOUT == 30


def test_config_empty_api_key_is_valid(monkeypatch):
    monkeypatch.setenv("VS_API_KEY", "")
    cfg = importlib.reload(config)
    assert cfg.VS_API_KEY == ""
