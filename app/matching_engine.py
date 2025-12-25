import asyncio
import json
import os
import sys
from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, update
from models import Order

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost:3306/orders")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def process_order_event(event):
    """Process ORDER_PLACED event and simulate matching"""
    try:
        data = json.loads(event.value.decode())
        
        if data["event"] == "ORDER_PLACED":
            print(f"📥 Received order #{data['order_id']} from user {data['user_id']}")
            
            # Simulate matching delay
            await asyncio.sleep(3)
            
            async with AsyncSessionLocal() as session:
                # Update order status
                stmt = update(Order).where(
                    Order.id == data["order_id"]
                ).values(status="FILLED")
                await session.execute(stmt)
                await session.commit()
                
                print(f"✅ Order #{data['order_id']} FILLED!")
    except Exception as e:
        print(f"❌ Error processing event: {e}")

async def main():
    print("🚀 Matching Engine started...")
    
    consumer = AIOKafkaConsumer(
        "order.events",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="matching-engine",
        auto_offset_reset="earliest"
    )
    
    await consumer.start()
    try:
        async for event in consumer:
            await process_order_event(event)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(main())
