# Prototipo · Iluminación de la biblioteca (SALA-02)

Proyecto final de **Herramientas de Desarrollo Profesional – TIC** (UTP). Trabajo individual.
**Autora:** Jeaneli Rosmery Caso Valenzuela · U22219824 · Caso 2: Biblioteca universitaria.

**Proceso mejorado:** ante una lectura baja de iluminación durante el horario de servicio, crear una solicitud de inspección para Mantenimiento.
**Regla:** incidente si `lux < 300` entre `08:00` (inclusive) y `20:00` (exclusivo), hora local de Lima. **KPI:** tiempo medio desde la medición baja hasta que la solicitud queda lista.

## Arquitectura
`Simulador (HTTP) → API FastAPI (regla + SQLite) → Tablero/Chatbot Streamlit (audio + Gemini) → aprobación humana → solicitud (SOL-xxx)`
Catálogo web (nginx) ← bot UiPath → `fichas.csv` → carga a la API. Agente UiPath → `POST /acciones/registrar-solicitud`.
IDs compartidos: `SALA-02` (equipo), `LEC-xxx` (lectura), `INC-xxx` (incidente), `SOL-xxx` (solicitud).

## Ejecutar (reproducible)
```bash
cp .env.example .env
docker compose up --build            # api :8000 · tablero/chatbot :8501 · catálogo :8080
python scripts/cargar_fichas.py data/fichas_rpa_ejemplo.csv   # o el CSV del bot (rpa/salida/fichas.csv)
python simulador/publicar_lecturas.py --fecha 2026-11-27 --pausa 1
```
Sin Docker: `pip install -r requirements.txt`, `uvicorn app.api:app` y `streamlit run app/ui.py`.
IA real: en `.env` pon `IA_MODO=gemini` y `GEMINI_API_KEY` (clave gratuita de Google AI Studio).

## Pruebas, seguridad e IaC
```bash
python -m pytest -q                      # 24 pruebas (reglas, API, IA, interfaz)
bandit -q -ll -r app simulador scripts   # control de seguridad
python scripts/validar_iac.py            # valida infra/sala02.k8s.yaml
python scripts/kpi.py                    # tiempo automatizado desde la base
IA_MODO=gemini python scripts/comparar_prompts.py   # zero-shot vs few-shot → docs/evidencia_prompts.md
```
Pipeline: `.github/workflows/ci.yml` (construir → pruebas + seguridad/IaC → despliegue simulado solo en `main` si todo pasa).

## Resultados esperados (casos de la rúbrica)
| Prueba | Entrada | Resultado |
|---|---|---|
| P01 normal | 380 lux a las 08:00 | solo historial |
| P02 fuera de umbral | 240 lux a las 13:00 | `INC-001`, JSON, aprobación, `SOL-001` |
| P03 excepción | `SALA-99` / ficha sin horario | excepción → revisión, sin usar otra ficha |
| — | 180 lux a las 20:15 | solo historial (fuera de horario) |

## Declaración de uso de IA y fuentes
Se empleó un asistente de IA generativa como apoyo para escribir y depurar código y documentación; las ejecuciones, mediciones, capturas y resultados fueron realizados y verificados por la autora. Servicios: Google Gemini (API), UiPath, GitHub Actions, Docker. Datos ficticios con fines académicos.
