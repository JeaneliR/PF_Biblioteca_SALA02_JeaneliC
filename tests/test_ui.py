from streamlit.testing.v1 import AppTest


def test_interfaz_carga_sin_errores():
    at = AppTest.from_file("../app/ui.py", default_timeout=30).run()
    assert not at.exception
