import json
import os
from fastapi import HTTPException

CONFIG_DIR = os.path.dirname(__file__)
ENV = os.getenv("LINCHAT_ENV", "development")
CONFIG_FILE = os.path.join(CONFIG_DIR, f"config.{ENV}.json")
DEFAULT_CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def _read_config() -> dict:
    """Load configuration from file and environment variables."""
    conf = {}
    config_path = CONFIG_FILE if os.path.exists(CONFIG_FILE) else DEFAULT_CONFIG_FILE
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            conf.update(json.load(f))
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        conf.setdefault("openrouter_api_key", env_key)
    env_model = os.getenv("OPENROUTER_MODEL")
    if env_model:
        conf.setdefault("openrouter_model", env_model)
    return conf


def _get_api_key() -> str:
    conf = _read_config()
    key = conf.get("openrouter_api_key")
    if not key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    return key


def _get_model() -> str:
    conf = _read_config()
    return conf.get("openrouter_model", "openai/gpt-3.5-turbo")
