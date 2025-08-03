from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database.connection import Base

class Integration(Base):
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    provider = Column(String(100), nullable=False)
    provider_account_id = Column(String(255))
    credentials_encrypted = Column(Text)
    status = Column(String(20), default='pending')
    last_sync_at = Column(DateTime)
    sync_frequency = Column(Integer, default=3600)
    error_message = Column(Text)
    settings = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="integrations")
