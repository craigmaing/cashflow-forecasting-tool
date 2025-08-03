from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database.connection import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    size_category = Column(String(50))
    timezone = Column(String(50), default="UTC")
    currency_code = Column(String(3), default="USD")
    fiscal_year_start = Column(Integer, default=1)
    settings = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    bank_accounts = relationship("BankAccount", back_populates="organization")
    transactions = relationship("Transaction", back_populates="organization")
    forecasts = relationship("Forecast", back_populates="organization")
    categories = relationship("Category", back_populates="organization")
    integrations = relationship("Integration", back_populates="organization")
    alerts = relationship("Alert", back_populates="organization")
