import importlib

import pytest
from propwatch.core import config


def reload_config_module(monkeypatch):
    """Reload the config module so class attributes reflect patched env vars."""
    try:
        import dotenv
    except ImportError:
        dotenv = None
    if dotenv:
        monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: None)
    return importlib.reload(config)


def test_config_validate_missing_env(monkeypatch):
    """Config.validate should complain when required vars are not set."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    reload_config_module(monkeypatch)

    with pytest.raises(ValueError) as exc_info:
        config.Config.validate()

    message = str(exc_info.value)
    assert "DATABASE_URL" in message
    assert "OPENAI_API_KEY" in message


def test_config_reads_env_and_validates(monkeypatch):
    """Config should load env vars and pass validation when they exist."""
    monkeypatch.setenv("DATABASE_URL", "postgres://localhost/test")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    monkeypatch.setenv("REPORT_OUTPUT_PATH", "./reports-out")

    reload_config_module(monkeypatch)

    # Validation should not raise with required env vars present.
    config.Config.validate()

    assert config.Config.DATABASE_URL == "postgres://localhost/test"
    assert config.Config.OPENAI_API_KEY == "fake-key"
    assert config.Config.REPORT_OUTPUT_PATH == "./reports-out"
