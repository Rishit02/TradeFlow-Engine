from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.kafka import init_kafka, close_kafka
from db.mysql import init_db
from routes.orders import router as orders_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()      # ← AUTO-CREATE TABLES
    # Startup
    await init_kafka()
    yield
    # Shutdown
    await close_kafka()


app = FastAPI(title="TradeFlow Engine", lifespan=lifespan)

# Include routers
app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}
