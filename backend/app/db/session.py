from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import AsyncSessionLocal

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
