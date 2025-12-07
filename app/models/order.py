# app/models/order.py
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # Add autoincrement=True
    user_id = Column(Integer, index=True)
    item = Column(String(255))
    amount = Column(DECIMAL(10,2))
