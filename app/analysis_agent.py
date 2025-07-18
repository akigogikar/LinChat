import os
import shutil
import subprocess
import tempfile
import json
from . import config
import openai


def generate_rust_code(prompt: str) -> str:
    """Use the LLM to generate Rust code for custom analysis."""
    openai.api_key = config._get_api_key()
    openai.base_url = "https://openrouter.ai/api/v1"
    messages = [
        {
            "role": "system",
            "content": (
                "Write a self-contained Rust program using the polars crate that reads the Excel file `input.xlsx` "
                "and prints a JSON string to stdout with the results of the requested analysis."),
        },
        {"role": "user", "content": prompt},
    ]
    completion = openai.ChatCompletion.create(model=config._get_model(), messages=messages)
    return completion.choices[0].message["content"]


def run_custom_analysis(file_path: str, prompt: str) -> dict:
    """Generate, compile, and run Rust analysis code."""
    code = generate_rust_code(prompt)
    temp_dir = tempfile.mkdtemp(prefix="analysis_agent_")
    try:
        src_dir = os.path.join(temp_dir, "src")
        os.makedirs(src_dir)
        with open(os.path.join(temp_dir, "Cargo.toml"), "w") as f:
            f.write(
                "[package]\nname = \"analysis_agent\"\nversion = \"0.1.0\"\nedition = \"2021\"\n"
                "[dependencies]\npolars = { version = \"0.49\", features = [\"lazy\"] }\nserde_json = \"1\"\ncalamine = \"0.28\"\n")
        with open(os.path.join(src_dir, "main.rs"), "w") as f:
            f.write(code)
        shutil.copy(file_path, os.path.join(temp_dir, "input.xlsx"))
        subprocess.run(["cargo", "build", "--release"], cwd=temp_dir, check=True)
        exe = os.path.join(temp_dir, "target", "release", "analysis_agent")
        output = subprocess.check_output([exe], cwd=temp_dir)
        return json.loads(output.decode())
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
