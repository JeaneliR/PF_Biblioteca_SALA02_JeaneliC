"""KPI: tiempo medio desde la lectura baja (recibida) hasta la solicitud lista, automatizado.
Los tiempos manuales se registran con cronómetro en la matriz. Uso: python scripts/kpi.py"""
import sys
from datetime import datetime

sys.path.insert(0, ".")
from app import db  # noqa: E402

with db.conexion() as c:
    filas = c.execute("""SELECT i.id inc, l.recibido_en t0, s.creado_en t1 FROM incidentes i
      JOIN lecturas l ON l.id=i.lectura_id JOIN solicitudes s ON s.incidente_id=i.id ORDER BY i.id""").fetchall()
tiempos = []
for f in filas:
    seg = (datetime.fromisoformat(f["t1"]) - datetime.fromisoformat(f["t0"])).total_seconds()
    tiempos.append(seg)
    print(f"{db.fmt_id('INC', f['inc'])}: {seg:.1f} s")
if tiempos:
    print(f"Promedio automatizado: {sum(tiempos)/len(tiempos):.1f} s ({len(tiempos)} incidencias)")
else:
    print("Aún no hay incidencias con solicitud registrada.")
