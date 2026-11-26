from app import ia

L = {"sala_id": "SALA-02", "lux": 240, "hora": "13:00"}


def test_prompts_usan_delimitadores_y_esquema():
    z, f = ia.prompt_zero_shot("sala oscura", L), ia.prompt_few_shot("sala oscura", L)
    assert "###" in z and "sala_id, lux, hora, resumen, destino" in z
    assert "Ejemplo 1" in f and "Ejemplo" not in z


def test_validacion_ok():
    r = ia.validar({**L, "resumen": "Poca luz en las mesas del centro", "destino": "Mantenimiento de sede"}, L)
    assert r["valido"]


def test_validacion_detecta_lux_distinto_y_destino_invalido():
    mal = ia.validar({**L, "lux": 500, "resumen": "Poca luz en la sala", "destino": "Mantenimiento de sede"}, L)
    assert "lux_no_coincide" in mal["errores"]
    mal2 = ia.validar({**L, "resumen": "Poca luz en la sala", "destino": "Cocina"}, L)
    assert not mal2["valido"]


def test_limpiar_json_con_markdown():
    assert ia.limpiar_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_cadena_simulada_valida():
    r = ia.cadena("La sala está oscura", L)
    assert r["validacion"]["valido"] and r["clasificacion"] and r["accion_sugerida"]


def test_gemini_se_llama_por_api(monkeypatch):
    from app import config
    monkeypatch.setattr(config, "IA_MODO", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "x")

    class R:
        def raise_for_status(self): pass
        def json(self): return {"candidates": [{"content": {"parts": [{"text": '{"sala_id":"SALA-02","lux":240,"hora":"13:00","resumen":"Poca luz","destino":"Mantenimiento de sede"}'}]}}]}

    llamadas = []
    monkeypatch.setattr(ia.requests, "post", lambda url, **k: (llamadas.append(url), R())[1])
    out = ia.extraer("sala oscura", L)
    assert out["lux"] == 240 and "generativelanguage" in llamadas[0]
