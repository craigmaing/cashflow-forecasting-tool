from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database.connection import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    bank_account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"))
    transaction_date = Column(Date, nullable=False)
    posted_date = Column(Date)
    amount = Column(Numeric(15, 2), nullable=False)
    currency_code = Column(String(3), default="USD")
    transaction_type = Column(String(30), nullable=False)
    category = Column(String(100))
    description = Column(String)
    merchant_name = Column(String(255))
    reference_number = Column(String(100))
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(JSONB)
    tags = Column(String(255))
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="transactions")
    bank_account = relationship("BankAccount", back_populates="transactions")
