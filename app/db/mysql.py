import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/orders")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

async def init_db():
    from models import Base
    async with engine.begin() as conn: 
        await conn.run_sync(Base.metadata.create_all)
