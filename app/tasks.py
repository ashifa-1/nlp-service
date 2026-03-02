from celery import Celery
from .database import SessionLocal, update_task_status
from .nlp_models import load_nlp_models, perform_sentiment_analysis, perform_ner
from .config import settings
import logging

logger = logging.getLogger(__name__)

# initialize celery
celery_app = Celery('nlp_tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

NLP_MODELS = {}

@celery_app.on_after_configure.connect
def load_models_on_startup(sender, **kwargs):
    global NLP_MODELS
    NLP_MODELS = load_nlp_models()
    print("NLP models loaded in Celery worker.")

@celery_app.task(bind=True, default_retry_delay=300, max_retries=5)
def process_nlp_task(self, task_id: str, text: str, task_type: str):
    db = SessionLocal()
    try:
        update_task_status(db, task_id, "PROCESSING")

        result = None
        if task_type == "sentiment_analysis":
            if 'sentiment' not in NLP_MODELS:
                raise ValueError("Sentiment model not loaded")
            result = perform_sentiment_analysis(text, NLP_MODELS['sentiment'])
        elif task_type == "named_entity_recognition":
            if 'ner' not in NLP_MODELS:
                raise ValueError("NER model not loaded")
            result = perform_ner(text, NLP_MODELS['ner'])
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        update_task_status(db, task_id, "COMPLETED", result=result)
    except Exception as e:
        error_msg = f"NLP processing failed: {e}"
        logger.exception("task %s failed", task_id)
        update_task_status(db, task_id, "FAILED", error_message=error_msg)
        # re-raise to let celery record failure
        raise
    finally:
        db.close()
