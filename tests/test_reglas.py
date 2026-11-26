from datetime import datetime

import pytest

from app import reglas

H = "08:00 a 20:00"


def ts(h, m=0):
    return datetime.fromisoformat(f"2026-11-27T{h:02d}:{m:02d}:00-05:00")


@pytest.mark.parametrize("hora,lux,estado", [
    ((8, 0), 380, "HISTORIAL"),
    ((10, 30), 340, "HISTORIAL"),
    ((11, 0), 300, "HISTORIAL"),   # 300 no es menor que 300
    ((13, 0), 240, "ALERTA"),
    ((20, 15), 180, "HISTORIAL"),  # fuera de horario: solo historial
    ((8, 0), 299, "ALERTA"),       # 08:00 inclusive
    ((20, 0), 100, "HISTORIAL"),   # 20:00 exclusivo
    ((19, 59), 100, "ALERTA"),
])
def test_cinco_lecturas_y_bordes(hora, lux, estado):
    assert reglas.evaluar(lux, ts(*hora), H)["estado"] == estado


def test_ficha_sin_horario_va_a_revision():
    r = reglas.evaluar(240, ts(13), "")
    assert r["estado"] == "REVISION" and r["dato_faltante"] == "horario_servicio"


def test_zona_horaria_utc_se_convierte_a_lima():
    utc = datetime.fromisoformat("2026-11-27T18:00:00+00:00")  # 13:00 Lima
    assert reglas.evaluar(240, utc, H)["estado"] == "ALERTA"
