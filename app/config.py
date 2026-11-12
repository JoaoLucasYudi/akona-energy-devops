"""Configuração do app, lida somente de variáveis de ambiente."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str
    enable_error_simulation: bool


def load_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "local"),
        enable_error_simulation=os.environ.get("ENABLE_ERROR_SIMULATION", "false").strip().lower()
        == "true",
    )
