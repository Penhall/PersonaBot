#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import urllib.error
from dotenv import load_dotenv, find_dotenv


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read().decode("utf-8", errors="ignore")


def http_post_json(url: str, payload: dict, timeout: float = 15.0) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
        return resp.getcode(), json.loads(body)


def main() -> int:
    load_dotenv(find_dotenv(usecwd=True))

    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider != "ollama":
        print("[!] LLM_PROVIDER não é 'ollama'. Defina LLM_PROVIDER=ollama no .env para este teste.")
        return 2

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.1")

    # 1) Verifica conectividade com o serviço Ollama
    try:
        code, body = http_get(f"{base_url}/api/tags", timeout=5.0)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"[x] Falha ao conectar ao Ollama em {base_url}: {e}")
        print("    - Certifique-se de que o serviço Ollama está em execução.")
        print("    - No terminal: 'ollama serve' (ou abra o app no desktop).")
        return 1

    if code != 200:
        print(f"[x] Ollama respondeu com status {code} em /api/tags")
        return 1

    try:
        tags = json.loads(body)
    except json.JSONDecodeError:
        print("[x] Resposta inesperada de /api/tags (não é JSON válido)")
        return 1

    available = [t.get("name") for t in tags.get("models", [])]
    if model not in available:
        print(f"[!] Modelo '{model}' não encontrado no Ollama. Modelos disponíveis: {available}")
        print(f"    Dica: 'ollama pull {model}'")
        return 3

    # 2) Geração simples
    prompt = "Responda apenas: pong"
    try:
        code, resp = http_post_json(
            f"{base_url}/api/generate",
            {"model": model, "prompt": prompt, "stream": False},
            timeout=30.0,
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"[x] Falha na geração via Ollama: {e}")
        return 1

    if code != 200:
        print(f"[x] Falha na geração (status {code}): {resp}")
        return 1

    text = (resp or {}).get("response", "").strip().lower()
    if "pong" in text:
        print("[OK] Ollama respondeu com sucesso: ", resp.get("response", ""))
        return 0

    print("[!] Geração concluída mas resposta inesperada:")
    print(resp)
    return 4


if __name__ == "__main__":
    sys.exit(main())

