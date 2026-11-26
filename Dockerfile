FROM python:3.12-slim
WORKDIR /srv
ENV PYTHONPATH=/srv PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DB_PATH=/data/biblioteca.db AUDITORIA_PATH=/data/auditoria.jsonl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY .streamlit ./.streamlit
COPY scripts ./scripts
COPY simulador ./simulador
COPY data/fichas_rpa_ejemplo.csv ./data/fichas_rpa_ejemplo.csv
RUN useradd -m app && mkdir /data && chown app /data
USER app
EXPOSE 8000 8501
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')" || exit 0
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
