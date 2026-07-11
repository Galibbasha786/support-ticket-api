import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import relationship

from app.db import Base


def generate_uuid():
    return str(uuid.uuid4())


class Queue(Base):
    __tablename__ = "queues"

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    name = Column(String(32), unique=True, nullable=False, index=True)
    capacity = Column(Integer, nullable=False)
    current_ticket_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="queue", cascade="save-update, merge")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(CHAR(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    complexity = Column(Integer, nullable=False)
    queue_id = Column(CHAR(36), ForeignKey("queues.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    queue = relationship("Queue", back_populates="tickets")
