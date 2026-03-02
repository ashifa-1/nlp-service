import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import ProcessRequest
from app.database import create_task, get_task, SessionLocal, NLPTask

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    # drop and recreate tables for each test using in-memory or temp db; but here we'll just use session and delete
    db = SessionLocal()
    try:
        db.query(NLPTask).delete()
        db.commit()
    finally:
        db.close()


def test_process_endpoint_valid(monkeypatch):
    payload = {"text": "Hello world", "task_type": "sentiment_analysis"}
    response = client.post("/api/nlp/process", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data['status'] == 'PENDING'
    assert 'task_id' in data


def test_process_endpoint_invalid_type():
    payload = {"text": "text", "task_type": "unknown"}
    response = client.post("/api/nlp/process", json=payload)
    assert response.status_code == 422  # validation error from FastAPI


def test_status_not_found():
    response = client.get(f"/api/nlp/status/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_status_invalid_uuid():
    response = client.get(f"/api/nlp/status/not-a-uuid")
    assert response.status_code == 400


def test_db_functions():
    db = SessionLocal()
    try:
        task = create_task(db, "abc", "sentiment_analysis")
        fetched = get_task(db, task.task_id)
        assert fetched is not None
        assert fetched.input_text == "abc"
    finally:
        db.close()
