"""Regla de alerta: lux < umbral dentro del horario [inicio, fin) en hora local de la sede."""
from __future__ import annotations

import re
from datetime import datetime, time

from .config import TZ, UMBRAL_LUX

_HORARIO = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*(?:a|-|–)\s*(\d{1,2}):(\d{2})\s*$")


def parsear_horario(texto: str | None) -> tuple[time, time] | None:
    """'08:00 a 20:00' -> (time(8,0), time(20,0)). Devuelve None si falta o es inválido."""
    if not texto:
        return None
    m = _HORARIO.match(texto)
    if not m:
        return None
    h1, m1, h2, m2 = map(int, m.groups())
    try:
        return time(h1, m1), time(h2, m2)
    except ValueError:
        return None


def a_hora_local(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=TZ)
    return ts.astimezone(TZ)


def en_horario(ts: datetime, inicio: time, fin: time) -> bool:
    """Inicio inclusive, fin exclusivo."""
    t = a_hora_local(ts).time()
    return inicio <= t < fin


def evaluar(lux: float, ts: datetime, horario: str | None, umbral: float = UMBRAL_LUX) -> dict:
    """Devuelve estado: ALERTA | HISTORIAL | REVISION y el motivo."""
    rango = parsear_horario(horario)
    if rango is None:
        return {"estado": "REVISION", "motivo": "FICHA_SIN_HORARIO", "dato_faltante": "horario_servicio"}
    dentro = en_horario(ts, *rango)
    if not dentro:
        return {"estado": "HISTORIAL", "motivo": "FUERA_DE_HORARIO", "dato_faltante": None}
    if lux < umbral:
        return {"estado": "ALERTA", "motivo": "LUX_BAJO_EN_HORARIO", "dato_faltante": None}
    return {"estado": "HISTORIAL", "motivo": "LUX_NORMAL", "dato_faltante": None}
