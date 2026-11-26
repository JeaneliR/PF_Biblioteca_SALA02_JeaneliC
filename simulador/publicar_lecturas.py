"""Simulador de sensor: publica las 5 lecturas del caso por HTTP (POST /lecturas).
Uso: python simulador/publicar_lecturas.py [--api http://localhost:8000] [--fecha 2026-11-27] [--pausa 1]"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

LECTURAS = [("08:00", 380), ("10:30", 340), ("11:00", 300), ("13:00", 240), ("20:15", 180)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--api", default=os.getenv("API_URL", "http://localhost:8000"))
    p.add_argument("--clave", default=os.getenv("API_KEY", "clave-demo-ficticia"))
    p.add_argument("--sala", default="SALA-02")
    p.add_argument("--fecha", default=datetime.now(ZoneInfo("America/Lima")).strftime("%Y-%m-%d"))
    p.add_argument("--pausa", type=float, default=1.0)
    a = p.parse_args()
    salidas = []
    for hora, lux in LECTURAS:
        ts = f"{a.fecha}T{hora}:00-05:00"
        r = requests.post(f"{a.api}/lecturas", headers={"x-api-key": a.clave},
                          json={"sala_id": a.sala, "lux": lux, "timestamp": ts}, timeout=10)
        r.raise_for_status()
        d = r.json()
        salidas.append({"hora": hora, "lux": lux, **d})
        print(f"{hora} {lux:>4} lux -> {d['lectura_id']} {d['estado']:<9} {d['motivo']} {d['incidente_id'] or ''}")
        time.sleep(a.pausa)
    try:  # el resumen es opcional: en el contenedor la carpeta puede ser de solo lectura
        Path("data").mkdir(exist_ok=True)
        Path("data/ultima_publicacion.json").write_text(json.dumps(salidas, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        print("(no se guardó data/ultima_publicacion.json; no afecta a las lecturas)")


if __name__ == "__main__":
    sys.exit(main())
