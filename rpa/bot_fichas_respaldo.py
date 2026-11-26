"""Respaldo en Python del bot de UiPath: consulta la web de fichas, extrae campos y registra excepciones.
Uso: python rpa/bot_fichas_respaldo.py SALA-02 SALA-03 SALA-99 [--base http://localhost:8080]"""
import argparse
import csv
import os
import re
import urllib.error
import urllib.request
from datetime import datetime

CAMPOS = {"ficha-id": "sala_id", "ficha-nombre": "nombre", "ficha-horario": "horario", "ficha-responsable": "responsable"}


def extraer(html: str) -> dict:
    out = {}
    for ident, campo in CAMPOS.items():
        m = re.search(rf'id="{ident}">(.*?)</td>', html, re.S)
        out[campo] = m.group(1).strip() if m else ""
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("salas", nargs="+")
    p.add_argument("--base", default="http://localhost:8080")
    a = p.parse_args()
    os.makedirs("rpa/salida", exist_ok=True)
    fichas, excepciones = [], []
    for sala in a.salas:
        try:
            with urllib.request.urlopen(f"{a.base}/{sala}.html", timeout=10) as r:  # nosec B310
                ficha = extraer(r.read().decode("utf-8"))
            if ficha["sala_id"] != sala:
                raise ValueError("ID de ficha distinto al buscado")
            fichas.append(ficha)
            if not ficha["horario"]:
                excepciones.append({"sala_id": sala, "tipo": "FICHA_INCOMPLETA", "detalle": "falta horario"})
        except (urllib.error.URLError, ValueError) as e:
            excepciones.append({"sala_id": sala, "tipo": "FICHA_NO_ENCONTRADA", "detalle": str(e)})
    with open("rpa/salida/fichas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["sala_id", "nombre", "horario", "responsable"])
        w.writeheader(); w.writerows(fichas)
    with open("rpa/salida/excepciones.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ts", "sala_id", "tipo", "detalle"])
        w.writeheader()
        for e in excepciones:
            w.writerow({"ts": datetime.now().isoformat(timespec="seconds"), **e})
    print(f"{len(fichas)} fichas, {len(excepciones)} excepciones")


if __name__ == "__main__":
    main()
