from sqlalchemy import create_engine, Column, String, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NLPTask(Base):
    __tablename__ = "nlp_tasks"
    task_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    input_text = Column(Text, nullable=False)
    task_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_task(db_session, input_text, task_type) -> NLPTask:
    new_task = NLPTask(input_text=input_text, task_type=task_type)
    db_session.add(new_task)
    db_session.commit()
    db_session.refresh(new_task)
    return new_task


def get_task(db_session, task_id) -> NLPTask:
    return db_session.query(NLPTask).filter(NLPTask.task_id == task_id).first()


def update_task_status(db_session, task_id, status, result=None, error_message=None):
    task = get_task(db_session, task_id)
    if task:
        task.status = status
        task.result = result
        task.error_message = error_message
        db_session.commit()
        db_session.refresh(task)
    return task
