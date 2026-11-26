"""Carga en la base el CSV exportado por el bot de UiPath (rpa/salida/fichas.csv).
Columnas: sala_id,nombre,horario,responsable[,cola]. Uso: python scripts/cargar_fichas.py rpa/salida/fichas.csv"""
import csv
import sys

sys.path.insert(0, ".")
from app import db  # noqa: E402

ruta = sys.argv[1] if len(sys.argv) > 1 else "data/fichas_rpa_ejemplo.csv"
with open(ruta, encoding="utf-8-sig", newline="") as f:
    filas = [{k.strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]
print(f"{db.cargar_fichas(filas)} fichas cargadas desde {ruta}")
