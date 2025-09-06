from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from .database import Base

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    sent_date = Column(DateTime, nullable=False)
    sentiment = Column(String(50))
    sentiment_confidence = Column(Float)
    priority = Column(String(50))
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, nullable=False)
    generated_response = Column(Text, nullable=False)
    final_response = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    is_sent = Column(Integer, default=0)  # 0 = not sent, 1 = sent
