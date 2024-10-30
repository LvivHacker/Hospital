from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create the Base
Base = declarative_base()

# Define async engine
async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,  # This should use asyncpg
    echo=True
)

# Define async session
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)