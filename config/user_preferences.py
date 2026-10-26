import json
import os
from pathlib import Path


DEFAULT_FINALIZAR_OS_PREFERENCES = {
    "atendente": "Guilherme Brito Souza Santos",
    "mensagem_conclusao": "providenciado",
}


def _preferences_path():
    app_data = os.environ.get("APPDATA")
    if app_data:
        base_path = Path(app_data)
    else:
        base_path = Path.home() / "AppData" / "Roaming"

    return base_path / "AutomacaoRunrun" / "preferencias.json"


def carregar_preferencias_finalizar_os():
    path = _preferences_path()
    if not path.exists():
        return DEFAULT_FINALIZAR_OS_PREFERENCES.copy()

    with path.open("r", encoding="utf-8") as preferences_file:
        preferences = json.load(preferences_file)

    if not isinstance(preferences, dict):
        raise ValueError("O arquivo de preferências possui formato inválido.")

    return {
        key: preferences.get(key, default)
        if isinstance(preferences.get(key, default), str)
        else default
        for key, default in DEFAULT_FINALIZAR_OS_PREFERENCES.items()
    }


def salvar_preferencias_finalizar_os(atendente, mensagem_conclusao):
    preferences = {
        "atendente": atendente.strip(),
        "mensagem_conclusao": mensagem_conclusao.strip(),
    }
    if not all(preferences.values()):
        raise ValueError("Atendente e mensagem de conclusão são obrigatórios.")

    path = _preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as preferences_file:
        json.dump(preferences, preferences_file, ensure_ascii=False, indent=2)
