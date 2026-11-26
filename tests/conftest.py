import pytest

from app import config, db


@pytest.fixture(autouse=True)
def entorno(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setattr(config, "AUDITORIA_PATH", str(tmp_path / "aud.jsonl"))
    monkeypatch.setattr(config, "IA_MODO", "simulado")
    db.cargar_fichas([
        {"sala_id": "SALA-02", "nombre": "Sala 02", "horario": "08:00 a 20:00", "responsable": "Mantenimiento de sede"},
        {"sala_id": "SALA-03", "nombre": "Sala 03", "horario": "", "responsable": "Mantenimiento de sede"},
    ])
    yield
