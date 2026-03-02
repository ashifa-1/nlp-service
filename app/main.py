from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import ProcessRequest, ProcessResponse, StatusResponse
from .database import get_db, create_task, get_task
from .tasks import process_nlp_task
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

# simple health check
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/nlp/process", response_model=ProcessResponse, status_code=status.HTTP_202_ACCEPTED)
def submit_task(request: ProcessRequest, db: Session = Depends(get_db)):
    try:
        task = create_task(db, request.text, request.task_type)
    except Exception as e:
        logger.exception("error creating task")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to create task")

    # enqueue celery task
    try:
        process_nlp_task.delay(str(task.task_id), request.text, request.task_type)
    except Exception as exc:
        logger.exception("failed to send task to queue")
        # do not expose details to client
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Could not queue NLP task")

    return ProcessResponse(task_id=task.task_id, status=task.status)

@app.get("/api/nlp/status/{task_id}", response_model=StatusResponse)
def get_status(task_id: str, db: Session = Depends(get_db)):
    # validate uuid
    try:
        uuid_obj = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task_id format")

    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return StatusResponse(
        task_id=task.task_id,
        status=task.status,
        result=task.result,
        error_message=task.error_message,
        updated_at=task.updated_at.isoformat() if task.updated_at else None
    )
