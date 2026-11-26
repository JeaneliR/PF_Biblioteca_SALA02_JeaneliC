# Bot web en UiPath (Unidad 4): consultar la ficha de la sala

**Qué hace el bot:** abre `http://localhost:8080` (catálogo del repo), busca cada sala, extrae `sala_id`, `nombre`, `horario`, `responsable` y escribe `rpa/salida/fichas.csv`; si la ficha no existe o está incompleta registra una fila en `rpa/salida/excepciones.csv`. **Decisión que conserva el operador:** aprobar la solicitud (la toma el humano, no el bot).

**Por qué es candidata a RPA:** tarea repetitiva, basada en reglas, sin API (hoy se hace buscando a mano en la web) y con un resultado verificable.

## Pasos en UiPath Studio (reutiliza el flujo de PA4)
1. Levanta el catálogo: `docker compose up catalogo` (o `python -m http.server 8080` dentro de `catalogo_web`).
2. Nuevo proyecto *Process* → `Main.xaml` (puedes duplicar el de PA4 `Bot_Catalogo_Publico.xaml`).
3. `Read CSV` o un `Build Data Table` con la lista de IDs: `SALA-02`, `SALA-03`, `SALA-99` (esta última es la prueba P03).
4. `For Each` sobre las salas → `Use Application/Browser` abre `http://localhost:8080/<ID>.html`.
5. `Get Text` con los selectores por `id`: `ficha-id`, `ficha-nombre`, `ficha-horario`, `ficha-responsable` (están en el HTML a propósito).
6. `Try Catch`: si la página da 404 (SALA-99) → agregar fila a la tabla de excepciones (`FICHA_NO_ENCONTRADA`). Si `ficha-horario` viene vacío → `FICHA_INCOMPLETA`. **Nunca** reemplazar con la ficha de otra sala.
7. `Write CSV` de ambas tablas en `rpa/salida/`.
8. Captura: flujo en Studio, ejecución exitosa y los dos CSV.
9. Carga las fichas al sistema: `python scripts/cargar_fichas.py rpa/salida/fichas.csv`.

**Plan B (si UiPath falla el día de la demo):** `python rpa/bot_fichas_respaldo.py SALA-02 SALA-03 SALA-99` genera exactamente los mismos CSV. Dilo en voz alta: es el respaldo, no el bot de UiPath.
