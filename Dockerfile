FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    MALLOC_TRIM_THRESHOLD_=65536 \
    DOCKER_CONTAINER=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py run.py ./
COPY .streamlit/ ./.streamlit/
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY pages/ ./pages/
COPY tools/ ./tools/
COPY docs/ ./docs/
COPY openspec/ ./openspec/
COPY churrascontrol.db* ./

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/_stcore/health')" || exit 1

CMD ["python", "run.py"]

