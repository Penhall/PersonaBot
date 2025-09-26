import yaml
from pathlib import Path

def load_persona_config() -> dict:
    """Carrega as configurações de persona do arquivo YAML."""
    config_path = Path(__file__).parent.parent / "config" / "persona.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo de persona não encontrado em: {config_path}")
    except Exception as e:
        raise e
