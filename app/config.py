from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+mysqlconnector://user:password@db:3306/nlp_db"
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "db+" + DATABASE_URL

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
