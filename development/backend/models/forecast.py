from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database.connection import Base

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String)
    forecast_start_date = Column(DateTime, nullable=False)
    forecast_end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='draft')
    model_version = Column(String(50))
    confidence = Column(String(20), default='medium')
    parameters = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="forecasts")
    data_points = relationship("ForecastDataPoint", back_populates="forecast")

class ForecastDataPoint(Base):
    __tablename__ = "forecast_data_points"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("forecasts.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    predicted_inflow = Column(Numeric(15, 2))
    predicted_outflow = Column(Numeric(15, 2))
    predicted_balance = Column(Numeric(15, 2))
    confidence_score = Column(Numeric(5, 4))
    model_features = Column(JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    forecast = relationship("Forecast", back_populates="data_points")
