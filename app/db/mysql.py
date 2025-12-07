# app/db/mysql.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost/orders")

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
