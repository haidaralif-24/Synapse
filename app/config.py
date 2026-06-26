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


def get_api_key() -> str:
    try:
        import keyring
        key = keyring.get_password("fetchy", "api_key")
        if key:
            return key
    except Exception:
        pass
    config = load_config()
    return config.get("api_key", "")


def set_api_key(key: str):
    try:
        import keyring
        keyring.set_password("fetchy", "api_key", key)
        return
    except Exception:
        pass
    config = load_config()
    config["api_key"] = key
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
