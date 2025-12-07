# app/db/redis.py
import os
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis = aioredis.from_url(
    REDIS_URL,
    decode_responses=True,
    max_connections=20,
    socket_timeout=2,
    retry_on_timeout=True,
)
