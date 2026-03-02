from app.tasks import celery_app

# This module ensures the celery_app object is importable by the worker

if __name__ == "__main__":
    celery_app.start()