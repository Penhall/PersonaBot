from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict
import concurrent.futures as futures

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yaml

from dotenv import load_dotenv, find_dotenv

from src.service.personabot_service import run_single_interaction, run_single_interaction_with_persona


load_dotenv(find_dotenv(usecwd=True), override=False)

app = FastAPI(title="PersonaBot UI", version="0.1.0")

# Servir assets estáticos (index.html + css/js)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def index() -> Any:
    html_path = static_dir / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="index.html não encontrado")
    return html_path.read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


class AskRequest(BaseModel):
    question: str


@app.post("/api/ask")
def api_ask(payload: AskRequest) -> Dict[str, Any]:
    try:
        answer = run_single_interaction(payload.question)
        return {"ok": True, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Persona config endpoints
PERSONA_PATH = Path(__file__).parents[2] / "config" / "persona.yaml"
PERSONAS_DIR = Path(__file__).parents[2] / "config" / "personas"


@app.get("/api/persona")
def get_persona() -> Dict[str, Any]:
    if not PERSONA_PATH.exists():
        return {"ok": False, "error": "persona.yaml não encontrado"}
    data = yaml.safe_load(PERSONA_PATH.read_text(encoding="utf-8"))
    return {"ok": True, "persona": data}


class PersonaUpdate(BaseModel):
    persona: Dict[str, Any]


@app.post("/api/persona")
def update_persona(payload: PersonaUpdate) -> Dict[str, Any]:
    PERSONA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PERSONA_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload.persona, f, allow_unicode=True, sort_keys=False)
    return {"ok": True}


# Presets de personas (default + arquivos em config/personas)
def _load_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@app.get("/api/personas/presets")
def list_persona_presets() -> Dict[str, Any]:
    presets: list[Dict[str, Any]] = []
    # Default persona
    if PERSONA_PATH.exists():
        try:
            data = _load_yaml(PERSONA_PATH)
            presets.append({"key": "default", "name": data.get("name", "Default"), "path": str(PERSONA_PATH)})
        except Exception:
            presets.append({"key": "default", "name": "Default", "path": str(PERSONA_PATH)})
    # Extra personas
    if PERSONAS_DIR.exists():
        for p in sorted(PERSONAS_DIR.glob("*.yaml")):
            try:
                data = _load_yaml(p)
                presets.append({"key": p.stem, "name": data.get("name", p.stem), "path": str(p)})
            except Exception:
                presets.append({"key": p.stem, "name": p.stem, "path": str(p)})
    return {"ok": True, "presets": presets}


@app.get("/api/personas/{key}")
def get_persona_by_key(key: str) -> Dict[str, Any]:
    # suporte especial para a key 'default'
    if key == "default":
        path = PERSONA_PATH
    else:
        if any(ch in key for ch in ("/", "\\")):
            raise HTTPException(status_code=400, detail="key inválida")
        path = PERSONAS_DIR / f"{key}.yaml"
    if not path.exists():
        return {"ok": False, "error": "persona não encontrada"}
    try:
        data = _load_yaml(path)
        return {"ok": True, "persona": data, "path": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/personas/{key}")
def update_persona_by_key(key: str, payload: PersonaUpdate) -> Dict[str, Any]:
    if key == "default":
        path = PERSONA_PATH
    else:
        if any(ch in key for ch in ("/", "\\")):
            raise HTTPException(status_code=400, detail="key inválida")
        path = PERSONAS_DIR / f"{key}.yaml"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(payload.persona, f, allow_unicode=True, sort_keys=False)
        return {"ok": True, "path": str(path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PersonaCreate(BaseModel):
    key: str
    persona: Dict[str, Any]
    overwrite: bool = False


@app.post("/api/personas")
def create_persona(payload: PersonaCreate) -> Dict[str, Any]:
    key = payload.key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="key obrigatória")
    if key == "default" or any(ch in key for ch in ("/", "\\")):
        raise HTTPException(status_code=400, detail="key inválida")
    path = PERSONAS_DIR / f"{key}.yaml"
    try:
        if path.exists() and not payload.overwrite:
            raise HTTPException(status_code=409, detail="Persona já existe. Use overwrite=true para substituir.")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(payload.persona, f, allow_unicode=True, sort_keys=False)
        return {"ok": True, "path": str(path)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AskMultiRequest(BaseModel):
    question: str
    persona_keys: list[str] | None = None  # "default" e/ou nomes de arquivos em config/personas (sem .yaml)


@app.post("/api/ask-multi")
def api_ask_multi(payload: AskMultiRequest) -> Dict[str, Any]:
    # Mapeia keys para paths
    keys = payload.persona_keys or ["default"]
    results: dict[str, str] = {}

    # Resolve personas
    key_to_path: dict[str, Path] = {}
    if "default" in keys:
        key_to_path["default"] = PERSONA_PATH
    for k in keys:
        if k == "default":
            continue
        key_to_path[k] = PERSONAS_DIR / f"{k}.yaml"

    def _do(k: str, path: Path) -> tuple[str, str]:
        if not path.exists():
            return k, "[erro] persona não encontrada"
        try:
            persona = _load_yaml(path)
            ans = run_single_interaction_with_persona(payload.question, persona)
            return k, ans
        except Exception as e:
            return k, f"[erro] {e}"

    # Executa em paralelo para acelerar múltiplas personas
    with futures.ThreadPoolExecutor(max_workers=min(8, max(1, len(key_to_path)))) as ex:
        for k, ans in ex.map(lambda item: _do(*item), key_to_path.items()):
            results[k] = ans

    return {"ok": True, "answers": results}


# Env (.env) endpoints (somente chaves conhecidas)
ENV_PATH = Path(find_dotenv(usecwd=True) or ".env")
ENV_KEYS = [
    "LLM_PROVIDER",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
    "LLM_TEMPERATURE",
    "LLM_TOP_P",
    "LLM_MAX_TOKENS",
    "USE_RAG_TOOL",
]


def parse_env_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    data: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" in s:
            k, v = s.split("=", 1)
            data[k.strip()] = v.strip()
    return data


def write_env_file(path: Path, updates: Dict[str, str]) -> None:
    current = parse_env_file(path)
    current.update({k: v for k, v in updates.items() if k in ENV_KEYS})
    lines = [f"{k}={current[k]}" for k in current]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@app.get("/api/env")
def get_env() -> Dict[str, Any]:
    values = {k: os.getenv(k) for k in ENV_KEYS}
    return {"ok": True, "env": values, "env_file": str(ENV_PATH)}


class EnvUpdate(BaseModel):
    env: Dict[str, str]


@app.post("/api/env")
def update_env(payload: EnvUpdate) -> Dict[str, Any]:
    ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_env_file(ENV_PATH, payload.env)
    return {"ok": True}


# Credentials endpoints (YAML)
CRED_PATH = Path(__file__).parents[2] / "config" / "credentials.yaml"


@app.get("/api/credentials")
def get_credentials() -> Dict[str, Any]:
    if not CRED_PATH.exists():
        return {"ok": True, "credentials": None, "note": "Arquivo não encontrado."}
    data = yaml.safe_load(CRED_PATH.read_text(encoding="utf-8"))
    return {"ok": True, "credentials": data}


class CredentialsUpdate(BaseModel):
    credentials: Dict[str, Any]


@app.post("/api/credentials")
def update_credentials(payload: CredentialsUpdate) -> Dict[str, Any]:
    CRED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CRED_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload.credentials, f, allow_unicode=True, sort_keys=False)
    return {"ok": True}
