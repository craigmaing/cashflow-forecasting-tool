from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.connection import Database
from models.integration import Integration

router = APIRouter()

@router.get("/")
async def get_integrations(organization_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(Integration).where(Integration.organization_id == organization_id))
    integrations = result.scalars().all()
    return integrations

@router.post("/")
async def create_integration(integration_data: dict, session: AsyncSession = Depends(Database.get_session)):
    new_integration = Integration(**integration_data)
    session.add(new_integration)
    await session.commit()
    await session.refresh(new_integration)
    return new_integration
