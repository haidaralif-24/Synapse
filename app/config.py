import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".fetchy"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    _ensure_config_dir()
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    _ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def _keyring_credential(provider: str) -> str:
    return f"api_key_{provider}"


def get_api_key(provider: str = "") -> str:
    """Return the API key for *provider*, falling back to the legacy global key."""
    if provider:
        try:
            import keyring
            key = keyring.get_password("fetchy", _keyring_credential(provider))
            if key:
                return key
        except Exception:
            pass
        config = load_config()
        per_provider = config.get("api_keys", {})
        if provider in per_provider:
            return per_provider[provider]
    # legacy global fallback
    try:
        import keyring
        key = keyring.get_password("fetchy", "api_key")
        if key:
            return key
    except Exception:
        pass
    return load_config().get("api_key", "")


def set_api_key(provider: str, key: str):
    """Persist *key* for *provider*."""
    try:
        import keyring
        keyring.set_password("fetchy", _keyring_credential(provider), key)
        return
    except Exception:
        pass
    config = load_config()
    per_provider = config.setdefault("api_keys", {})
    per_provider[provider] = key
    save_config(config)


def get_provider() -> str:
    return load_config().get("provider", "openai")


def set_provider(provider: str):
    config = load_config()
    config["provider"] = provider
    save_config(config)


def get_model() -> str:
    return load_config().get("model", "")


def set_model(model: str):
    config = load_config()
    config["model"] = model
    save_config(config)


PROVIDER_DEFAULTS = {
    "openai": "gpt-4o",
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash",
}


def default_model_for(provider: str) -> str:
    return PROVIDER_DEFAULTS.get(provider, "gpt-4o")
