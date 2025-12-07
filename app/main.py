from fastapi import FastAPI
from routes.orders import router as orders_router

app = FastAPI()
app.include_router(orders_router, prefix="/orders")
