# Asynchronous NLP Service

An asynchronous backend for natural language processing tasks using FastAPI, Celery, RabbitMQ, and MySQL. This service accepts text-based tasks via a REST API, queues them for background execution, and provides status/result retrieval endpoints. It's containerized and meant to demonstrate scalable, event-driven Al infrastructure.

## Features

-  Sentiment analysis and named entity recognition (NER) using HuggingFace transformers
-  FastAPI REST endpoints for task submission and status polling
-  Celery with RabbitMQ for asynchronous task processing
-  MySQL for persistent task metadata storage via SQLAlchemy
-  Fully containerized with Docker & docker-compose
-  Unit and integration tests using pytest

## Quickstart

1. Clone the repository:
   ```bash
   git clone https://github.com/ashifa-1/nlp-service.git
   cd nlp-service
   ```
2. Copy env example and adjust variables:
   ```bash
   cp .env.example .env
   ```
3. Start all services:
   ```bash
   docker-compose up --build
   ```

The FastAPI app will be available at `http://localhost:8000` and Swagger UI at `http://localhost:8000/docs`.

> **Note:** the `test` service defined in docker-compose runs the full pytest suite inside the container, allowing automated CI tools to verify functionality with `docker-compose run test`.

## API Usage

### Submit a task

```bash
curl -X POST http://localhost:8000/api/nlp/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple is buying a startup", "task_type": "sentiment_analysis"}'
```

Response:
```json
{ "task_id": "<uuid>", "status": "PENDING" }
```

### Check status

```bash
curl http://localhost:8000/api/nlp/status/<task_id>
```

Possible responses:
```json
{ "task_id": "...", "status": "COMPLETED", "result": {...}, "updated_at": "..." }
```

or for failures:
```json
{ "task_id": "...", "status": "FAILED", "error_message": "..." }
```

## Architecture Overview

The system consists of four main components connected via a shared Docker network:

1. **FastAPI application** - a lightweight Python web server exposing REST endpoints (`/api/nlp/process`, `/api/nlp/status/{task_id}`) and performing input validation. It creates database records and publishes tasks to the queue.
2. **Celery worker** - one or more workers listening on RabbitMQ, executing NLP jobs asynchronously. Models are pre-loaded on startup to optimize performance.
3. **RabbitMQ broker** - reliable AMQP message queue used by Celery for task distribution. Tasks are acknowledged only after successful execution.
4. **MySQL database** - central store for task metadata (UUID, text, type, status, results, error messages, timestamps), accessed via SQLAlchemy. Both the API and workers share this database.

> A diagram could be inserted here showing arrows from FastAPI to RabbitMQ and DB, and RabbitMQ to Celery, with DB as shared storage.

Docker Compose orchestrates all services on a single network.

## NLP Tasks

- **Sentiment analysis**: `distilbert-base-uncased-finetuned-sst-2-english` via HuggingFace pipeline
- **Named Entity Recognition**: `dbmdz/bert-large-cased-finetuned-conll03-english` via pipeline

Models are loaded once per Celery worker process on startup for efficiency.

## Testing

Run tests inside container or locally:

```bash
# inside project root
pytest
```

Docker Compose also provides a `test` service (see `docker-compose.yml`) to run the suite.

## Deployment

Use the provided `docker-compose.yml` to deploy all components together. Ensure environment variables are set (via `.env`).
