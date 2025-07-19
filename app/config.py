import json
import os
CONFIG_DIR = os.path.dirname(__file__)
ENV = os.getenv("LINCHAT_ENV", "development")
CONFIG_FILE = os.path.join(CONFIG_DIR, f"config.{ENV}.json")
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def _read_config() -> dict:
    """Load configuration from file and environment variables."""
    conf: dict = {}

    config_path = CONFIG_FILE if os.path.exists(CONFIG_FILE) else DEFAULT_CONFIG_FILE
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            conf.update(json.load(f))
    env_user = os.getenv("ADMIN_USERNAME")
    if env_user:
        conf.setdefault("admin_username", env_user)
    env_password = os.getenv("ADMIN_PASSWORD")
    if env_password:
        conf.setdefault("admin_password", env_password)
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        conf.setdefault("openrouter_api_key", env_key)
    env_model = os.getenv("OPENROUTER_MODEL")
    if env_model:
        conf.setdefault("openrouter_model", env_model)
    return conf


def _write_config(conf: dict) -> None:
    """Persist configuration to disk."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(conf, f, indent=2)


def set_openrouter_credentials(key: str, model: str | None = None) -> None:
    """Persist OpenRouter API credentials using the config helpers."""
    conf = _read_config()
    conf["openrouter_api_key"] = key
    if model is not None:
        conf["openrouter_model"] = model
    _write_config(conf)


def has_openrouter_key() -> bool:
    """Check if an API key is configured without exposing it."""
    conf = _read_config()
    return bool(conf.get("openrouter_api_key"))


def _get_api_key() -> str:
    conf = _read_config()
    key = conf.get("openrouter_api_key")
    if not key:
        raise RuntimeError("OpenRouter API key not configured")

    return key


def _get_model() -> str:
    conf = _read_config()
    return conf.get("openrouter_model", "openai/gpt-3.5-turbo")
