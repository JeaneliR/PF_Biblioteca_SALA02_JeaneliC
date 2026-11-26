"""Función de productividad: registra la solicitud de inspección SOLO con aprobación humana.
La usan el chatbot (Streamlit) y el agente de UiPath (vía POST /acciones/registrar-solicitud)."""
import json

from . import auditoria, db


class AprobacionRequerida(Exception):
    pass


def registrar_solicitud(incidente_id: str, aprobado_por: str, aprobado: bool, payload_ia: dict | None = None) -> dict:
    if not aprobado or not (aprobado_por or "").strip():
        auditoria.registrar("SOLICITUD_BLOQUEADA", incidente_id=incidente_id, motivo="sin aprobación humana")
        raise AprobacionRequerida("Se requiere aprobación humana explícita")
    n = db.num(incidente_id)
    with db.conexion() as c:
        inc = c.execute("SELECT * FROM incidentes WHERE id=?", (n,)).fetchone()
        if inc is None:
            raise KeyError(incidente_id)
        if inc["estado"] == "SOLICITUD_REGISTRADA":
            raise ValueError("El incidente ya tiene solicitud")
        payload = payload_ia or db.json_o_none(inc["payload_ia"]) or {}
        ficha = c.execute("SELECT * FROM fichas WHERE sala_id=?", (inc["sala_id"],)).fetchone()
        destino = payload.get("destino") or (ficha["responsable"] if ficha else "Mantenimiento de sede")
        creado = db.ahora()
        cur = c.execute(
            "INSERT INTO solicitudes(incidente_id,sala_id,destino,aprobado_por,creado_en,detalle) VALUES(?,?,?,?,?,?)",
            (n, inc["sala_id"], destino, aprobado_por, creado, json.dumps(payload, ensure_ascii=False)),
        )
        c.execute("UPDATE incidentes SET estado='SOLICITUD_REGISTRADA' WHERE id=?", (n,))
        sol_id = db.fmt_id("SOL", cur.lastrowid)
    return auditoria.registrar(
        "SOLICITUD_REGISTRADA", solicitud_id=sol_id, incidente_id=incidente_id,
        sala_id=inc["sala_id"], destino=destino, aprobado_por=aprobado_por,
    )
