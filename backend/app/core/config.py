import os

DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC", "postgresql+asyncpg://postgres:postgres@localhost:5433/Hospital")
DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC", "postgresql+psycopg2://postgres:postgres@localhost:5433/Hospital")

class Settings:
    DATABASE_URL_ASYNC = DATABASE_URL_ASYNC
    DATABASE_URL_SYNC = DATABASE_URL_SYNC

settings = Settings()
