from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.connection import Database
from models.alert import Alert

router = APIRouter()

@router.get("/")
async def get_alerts(organization_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(Alert).where(Alert.organization_id == organization_id))
    alerts = result.scalars().all()
    return alerts

@router.post("/")
async def create_alert(alert_data: dict, session: AsyncSession = Depends(Database.get_session)):
    new_alert = Alert(**alert_data)
    session.add(new_alert)
    await session.commit()
    await session.refresh(new_alert)
    return new_alert

@router.patch("/{alert_id}/read")
async def mark_alert_read(alert_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    await session.commit()
    return {"status": "marked_read"}
