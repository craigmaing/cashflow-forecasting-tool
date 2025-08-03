from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.connection import Database
from models.user import User

router = APIRouter()

@router.get("/{user_id}")
async def get_user(user_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/")
async def get_users(organization_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(User).where(User.organization_id == organization_id))
    users = result.scalars().all()
    return users
