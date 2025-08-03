from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.connection import Database
from models.forecast import Forecast, ForecastDataPoint
from models.transaction import Transaction
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/{organization_id}/generate")
async def generate_forecast(
    organization_id: str,
    forecast_days: int = 30,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: AsyncSession = Depends(Database.get_session)
):
    # Create forecast record
    new_forecast = Forecast(
        organization_id=organization_id,
        created_by=organization_id,  # Simplified for now
        name=f"AI Forecast - {datetime.now().strftime('%Y-%m-%d')}",
        forecast_start_date=datetime.now(),
        forecast_end_date=datetime.now() + timedelta(days=forecast_days),
        status='active'
    )
    
    session.add(new_forecast)
    await session.commit()
    await session.refresh(new_forecast)
    
    # Queue background task to generate predictions
    background_tasks.add_task(generate_forecast_data, str(new_forecast.id), organization_id, forecast_days)
    
    return {"forecast_id": str(new_forecast.id), "status": "generating"}

@router.get("/{forecast_id}")
async def get_forecast(forecast_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(Forecast).where(Forecast.id == forecast_id))
    forecast = result.scalar()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    # Get data points
    data_result = await session.execute(
        select(ForecastDataPoint).where(ForecastDataPoint.forecast_id == forecast_id)
    )
    data_points = data_result.scalars().all()
    
    return {
        "forecast": forecast,
        "data_points": data_points
    }

async def generate_forecast_data(forecast_id: str, organization_id: str, forecast_days: int):
    # This would integrate with the AI forecasting engine
    # For now, generate dummy data
    import asyncio
    await asyncio.sleep(2)  # Simulate processing time
    
    async with Database.get_session() as session:
        for i in range(forecast_days):
            data_point = ForecastDataPoint(
                forecast_id=forecast_id,
                date=datetime.now() + timedelta(days=i+1),
                predicted_inflow=10000 + (i * 100),
                predicted_outflow=8000 + (i * 80),
                predicted_balance=2000 + (i * 20),
                confidence_score=0.85
            )
            session.add(data_point)
        
        await session.commit()
