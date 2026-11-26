"""API de ingesta: recibe lecturas, aplica la regla y abre incidentes."""
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import acciones, auditoria, config, db, reglas

app = FastAPI(title="Biblioteca · Iluminación SALA-02", version="1.0")


def clave(x_api_key: str = Header(default="")):
    if x_api_key != config.API_KEY:
        raise HTTPException(401, "API key inválida")


class LecturaIn(BaseModel):
    sala_id: str = Field(pattern=r"^SALA-\d{2}$")
    lux: float = Field(ge=0)
    timestamp: datetime


class AprobacionIn(BaseModel):
    incidente_id: str
    aprobado_por: str = ""
    aprobado: bool = False
    payload_ia: dict | None = None


@app.get("/health")
def health():
    return {"estado": "ok"}


@app.post("/lecturas", dependencies=[Depends(clave)])
def recibir_lectura(l: LecturaIn):
    ficha = db.obtener_ficha(l.sala_id)
    recibido = db.ahora()
    if ficha is None:
        estado = {"estado": "REVISION", "motivo": "SIN_FICHA", "dato_faltante": "ficha_completa"}
    else:
        estado = reglas.evaluar(l.lux, l.timestamp, ficha.get("horario"))
    with db.conexion() as c:
        cur = c.execute(
            "INSERT INTO lecturas(sala_id,lux,ts,recibido_en,estado,motivo) VALUES(?,?,?,?,?,?)",
            (l.sala_id, l.lux, reglas.a_hora_local(l.timestamp).isoformat(), recibido, estado["estado"], estado["motivo"]),
        )
        lec_id = cur.lastrowid
        inc_id = None
        if estado["estado"] == "ALERTA":
            ci = c.execute(
                "INSERT INTO incidentes(sala_id,lectura_id,estado,creado_en) VALUES(?,?,?,?)",
                (l.sala_id, lec_id, "PENDIENTE_APROBACION", recibido),
            )
            inc_id = db.fmt_id("INC", ci.lastrowid)
        elif estado["estado"] == "REVISION":
            c.execute(
                "INSERT INTO excepciones(sala_id,tipo,detalle,creado_en) VALUES(?,?,?,?)",
                (l.sala_id, estado["motivo"], f"dato faltante: {estado['dato_faltante']}", recibido),
            )
    auditoria.registrar("LECTURA", lectura_id=db.fmt_id("LEC", lec_id), sala_id=l.sala_id, lux=l.lux,
                        estado=estado["estado"], motivo=estado["motivo"], incidente_id=inc_id)
    return {"lectura_id": db.fmt_id("LEC", lec_id), "estado": estado["estado"], "motivo": estado["motivo"],
            "incidente_id": inc_id, "dato_faltante": estado["dato_faltante"]}


@app.get("/lecturas", dependencies=[Depends(clave)])
def lecturas():
    return db.listar("lecturas")


@app.get("/incidentes", dependencies=[Depends(clave)])
def incidentes():
    return db.listar("incidentes")


@app.post("/acciones/registrar-solicitud", dependencies=[Depends(clave)])
def registrar(a: AprobacionIn):
    try:
        return acciones.registrar_solicitud(a.incidente_id, a.aprobado_por, a.aprobado, a.payload_ia)
    except acciones.AprobacionRequerida as e:
        raise HTTPException(403, str(e))
    except KeyError:
        raise HTTPException(404, "Incidente no existe")
    except ValueError as e:
        raise HTTPException(409, str(e))
