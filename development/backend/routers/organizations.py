from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.connection import Database
from models.organization import Organization

router = APIRouter()

@router.post("/", response_model=dict)
async def create_organization(org_data: dict, session: AsyncSession = Depends(Database.get_session)):
    new_org = Organization(**org_data)
    session.add(new_org)
    await session.commit()
    await session.refresh(new_org)
    return {"id": str(new_org.id), "name": new_org.name}

@router.get("/{org_id}")
async def get_organization(org_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
