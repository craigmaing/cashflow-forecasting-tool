from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.connection import Database
from models.organization import Organization
from models.user import User

router = APIRouter()

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, session: AsyncSession = Depends(Database.get_session)):
    new_user = User(
        email=user.email,
        password_hash=user.password_hash,
        first_name=user.first_name,
        last_name=user.last_name,
        organization_id=user.organization_id
    )
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except IntegrityError:
        raise HTTPException(status_code=400, detail="User already registered.")

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

