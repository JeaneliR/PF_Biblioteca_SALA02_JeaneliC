from fastapi.testclient import TestClient

from app import config, db
from app.api import app

c = TestClient(app)
K = {"x-api-key": config.API_KEY}


def lectura(sala, lux, hora):
    return c.post("/lecturas", headers=K, json={"sala_id": sala, "lux": lux, "timestamp": f"2026-11-27T{hora}:00-05:00"}).json()


def test_p01_lectura_normal_solo_historial():
    r = lectura("SALA-02", 380, "08:00")
    assert r["estado"] == "HISTORIAL" and r["incidente_id"] is None


def test_p02_240_lux_a_las_13_abre_inc_001_y_exige_aprobacion():
    r = lectura("SALA-02", 240, "13:00")
    assert r["estado"] == "ALERTA" and r["incidente_id"] == "INC-001"
    sin = c.post("/acciones/registrar-solicitud", headers=K, json={"incidente_id": "INC-001"})
    assert sin.status_code == 403
    ok = c.post("/acciones/registrar-solicitud", headers=K,
                json={"incidente_id": "INC-001", "aprobado": True, "aprobado_por": "Encargada de biblioteca"})
    assert ok.status_code == 200 and ok.json()["solicitud_id"] == "SOL-001" and ok.json()["sala_id"] == "SALA-02"
    again = c.post("/acciones/registrar-solicitud", headers=K,
                   json={"incidente_id": "INC-001", "aprobado": True, "aprobado_por": "X"})
    assert again.status_code == 409


def test_180_lux_a_las_2015_solo_guarda_lectura():
    r = lectura("SALA-02", 180, "20:15")
    assert r["estado"] == "HISTORIAL" and r["motivo"] == "FUERA_DE_HORARIO" and r["incidente_id"] is None
    assert db.listar("incidentes") == []


def test_p03_sala_inexistente_registra_excepcion_sin_usar_otra_ficha():
    r = lectura("SALA-99", 240, "13:00")
    assert r["estado"] == "REVISION" and r["motivo"] == "SIN_FICHA"
    assert db.listar("excepciones")[0]["sala_id"] == "SALA-99"
    assert db.listar("incidentes") == []


def test_ficha_sin_horario_registra_dato_faltante():
    r = lectura("SALA-03", 240, "13:00")
    assert r["estado"] == "REVISION" and r["dato_faltante"] == "horario_servicio"
    assert "horario_servicio" in db.listar("excepciones")[0]["detalle"]


def test_sin_api_key_401():
    assert c.post("/lecturas", json={"sala_id": "SALA-02", "lux": 1, "timestamp": "2026-11-27T13:00:00-05:00"}).status_code == 401


def test_id_coincide_en_lectura_ficha_e_incidente():
    r = lectura("SALA-02", 240, "13:00")
    inc = db.listar("incidentes")[0]
    assert inc["sala_id"] == "SALA-02" == db.obtener_ficha("SALA-02")["sala_id"] == db.listar("lecturas")[0]["sala_id"]
