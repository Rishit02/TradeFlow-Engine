# app/db/kafka.py
import os
from aiokafka import AIOKafkaProducer

# Use service name inside Docker
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

producer = None

async def init_kafka():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()

async def close_kafka():
    global producer
    if producer:
        await producer.stop()

async def get_producer():
    return producer
