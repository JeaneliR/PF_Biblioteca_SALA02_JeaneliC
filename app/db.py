import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from . import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS fichas(
  sala_id TEXT PRIMARY KEY, nombre TEXT, horario TEXT, responsable TEXT, cola TEXT);
CREATE TABLE IF NOT EXISTS lecturas(
  id INTEGER PRIMARY KEY AUTOINCREMENT, sala_id TEXT, lux REAL, ts TEXT,
  recibido_en TEXT, estado TEXT, motivo TEXT);
CREATE TABLE IF NOT EXISTS incidentes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, sala_id TEXT, lectura_id INTEGER, estado TEXT,
  creado_en TEXT, payload_ia TEXT);
CREATE TABLE IF NOT EXISTS solicitudes(
  id INTEGER PRIMARY KEY AUTOINCREMENT, incidente_id INTEGER, sala_id TEXT,
  destino TEXT, aprobado_por TEXT, creado_en TEXT, detalle TEXT);
CREATE TABLE IF NOT EXISTS excepciones(
  id INTEGER PRIMARY KEY AUTOINCREMENT, sala_id TEXT, tipo TEXT, detalle TEXT, creado_en TEXT);
"""


@contextmanager
def conexion():
    import os
    os.makedirs(os.path.dirname(config.DB_PATH) or ".", exist_ok=True)
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    c.executescript(ESQUEMA)
    try:
        yield c
        c.commit()
    finally:
        c.close()


def ahora() -> str:
    return datetime.now(config.TZ).isoformat(timespec="milliseconds")


def fmt_id(prefijo: str, n: int) -> str:
    return f"{prefijo}-{n:03d}"


def num(id_texto: str) -> int:
    return int(id_texto.split("-")[-1])


def cargar_fichas(filas: list[dict]) -> int:
    with conexion() as c:
        for f in filas:
            c.execute(
                "INSERT OR REPLACE INTO fichas VALUES(?,?,?,?,?)",
                (f.get("sala_id"), f.get("nombre"), f.get("horario"), f.get("responsable"),
                 f.get("cola") or f.get("responsable")),
            )
    return len(filas)


def obtener_ficha(sala_id: str) -> dict | None:
    with conexion() as c:
        r = c.execute("SELECT * FROM fichas WHERE sala_id=?", (sala_id,)).fetchone()
        return dict(r) if r else None


_CONSULTAS = {
    "fichas": "SELECT * FROM fichas ORDER BY sala_id",
    "lecturas": "SELECT * FROM lecturas ORDER BY id",
    "incidentes": "SELECT * FROM incidentes ORDER BY id",
    "solicitudes": "SELECT * FROM solicitudes ORDER BY id",
    "excepciones": "SELECT * FROM excepciones ORDER BY id",
}


def listar(tabla: str) -> list[dict]:
    if tabla not in _CONSULTAS:
        raise ValueError("tabla no permitida")
    with conexion() as c:
        return [dict(r) for r in c.execute(_CONSULTAS[tabla])]


def json_o_none(s):
    return json.loads(s) if s else None
