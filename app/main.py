from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import openai
import json
import os

app = FastAPI()
security = HTTPBasic()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")


def _read_config():
    """Load configuration from file and environment variables."""
    conf = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
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
    return conf


def _write_config(conf: dict) -> None:
    """Persist configuration to disk."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(conf, f)


def _get_api_key() -> str:
    conf = _read_config()
    key = conf.get("openrouter_api_key")
    if not key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    return key


def _require_admin(credentials: HTTPBasicCredentials = Depends(security)):
    conf = _read_config()
    username = conf.get("admin_username", "admin")
    password = conf.get("admin_password")
    if not password:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    if credentials.username != username or credentials.password != password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.post("/query")
async def query_llm(prompt: str):
    """Query OpenRouter LLM with the given prompt."""
    openai.api_key = _get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"
    try:
        completion = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return {"response": completion.choices[0].message["content"]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/admin", response_class=HTMLResponse)
def admin_page(auth: bool = Depends(_require_admin)):
    conf = _read_config()
    key = conf.get("openrouter_api_key", "")
    return HTMLResponse(
        f"""<html><body>
        <h1>Admin Config</h1>
        <form action='/admin/set_key' method='post'>
            <label>OpenRouter API Key:</label><br/>
            <input type='text' name='key' value='{key}'/><br/>
            <input type='submit' value='Save'/>
        </form>
        </body></html>"""
    )


@app.post("/admin/set_key")
def set_key(key: str = Form(...), auth: bool = Depends(_require_admin)):
    conf = _read_config()
    conf["openrouter_api_key"] = key
    _write_config(conf)
    return {"status": "saved"}
