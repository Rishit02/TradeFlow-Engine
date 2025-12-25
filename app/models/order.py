from sqlalchemy import Column, Integer, String, DECIMAL, Enum
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from enum import Enum as PyEnum

Base = declarative_base()

class OrderStatus(PyEnum):
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    item = Column(String(255), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="OPEN", nullable=False)

    def __repr__(self) -> str:
        return f"Order(id={self.id}, user_id={self.user_id}, item={self.item}, amount={self.amount}, status={self.status})"
