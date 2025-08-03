from sqlalchemy import Column, String, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database.connection import Base

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    account_name = Column(String(255), nullable=False)
    account_number = Column(String(50))
    bank_name = Column(String(255))
    currency_code = Column(String(3), default="USD")
    current_balance = Column(Numeric(15, 2), default=0)
    available_balance = Column(Numeric(15, 2))
    last_synced_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="bank_account")
