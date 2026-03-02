# Dockerfile for FastAPI app and Celery worker services
FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# download spacy model during build to avoid runtime latency
RUN python -m spacy download en_core_web_sm || true

COPY app/ ./app/
COPY worker/ ./worker/
COPY init_db.py ./

# ensure database tables exist when container starts
ENTRYPOINT ["sh", "-c", "python init_db.py &&"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
