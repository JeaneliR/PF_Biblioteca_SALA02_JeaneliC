import os
from zoneinfo import ZoneInfo

TZ = ZoneInfo(os.getenv("TZ_SEDE", "America/Lima"))
UMBRAL_LUX = float(os.getenv("UMBRAL_LUX", "300"))
DB_PATH = os.getenv("DB_PATH", "data/biblioteca.db")
API_KEY = os.getenv("API_KEY", "clave-demo-ficticia")
API_URL = os.getenv("API_URL", "http://localhost:8000")
AUDITORIA_PATH = os.getenv("AUDITORIA_PATH", "data/auditoria.jsonl")
IA_MODO = os.getenv("IA_MODO", "simulado")  # simulado | gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
