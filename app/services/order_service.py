# app/services/order_service.py
from repositories.order_repo import OrderRepository
from db.redis import redis
import json


class OrderService:
    def __init__(self):
        self.repo = OrderRepository()

    async def create_order(self, order_in):
        order = await self.repo.create_order(order_in)

        # Invalidate cache for this user's order list
        await redis.delete(f"user:{order_in.user_id}:orders")

        return order

    async def get_user_orders(self, user_id: int):
        key = f"user:{user_id}:orders"

        # Try Redis cache first
        cached = await redis.get(key)
        if cached:
            return json.loads(cached)

        # Fallback to MySQL
        orders = await self.repo.get_orders_by_user(user_id)

        # Cache result
        await redis.set(key, json.dumps([o.__dict__ for o in orders]), ex=60)

        return orders
