import time
from fastapi.testclient import TestClient
from app.main import app
from app.tasks import process_nlp_task
from app.database import get_db
from sqlalchemy.orm import Session

client = TestClient(app)


def trigger_task_sync(task_id, text, task_type):
    # run the Celery task synchronously for testing
    process_nlp_task(task_id, text, task_type)


def test_end_to_end(monkeypatch):
    # intercept delay to run synchronously
    monkeypatch.setattr('app.main.process_nlp_task.delay', lambda tid, txt, ttype: trigger_task_sync(tid, txt, ttype))

    payload = {"text": "Apple is looking at buying U.K. startup for $1 billion", "task_type": "named_entity_recognition"}
    resp = client.post("/api/nlp/process", json=payload)
    assert resp.status_code == 202
    tid = resp.json()['task_id']

    # immediate status should be PENDING or COMPLETED depending on sync call
    status_resp = client.get(f"/api/nlp/status/{tid}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data['status'] in ("PROCESSING", "COMPLETED")
    # after some time it should be completed with result
    # call again to ensure result persisted
    status_resp = client.get(f"/api/nlp/status/{tid}")
    assert status_resp.json()['status'] == "COMPLETED"
    assert isinstance(status_resp.json().get('result'), list)
