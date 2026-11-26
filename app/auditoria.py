import json
import os

from . import config
from .db import ahora


def registrar(evento: str, **datos) -> dict:
    reg = {"ts": ahora(), "evento": evento, **datos}
    os.makedirs(os.path.dirname(config.AUDITORIA_PATH) or ".", exist_ok=True)
    with open(config.AUDITORIA_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    return reg
