from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.connection import Database
from models.bank_account import BankAccount

router = APIRouter()

@router.get("/")
async def get_accounts(organization_id: str, session: AsyncSession = Depends(Database.get_session)):
    result = await session.execute(select(BankAccount).where(BankAccount.organization_id == organization_id))
    accounts = result.scalars().all()
    return accounts

@router.post("/")
async def create_account(account_data: dict, session: AsyncSession = Depends(Database.get_session)):
    new_account = BankAccount(**account_data)
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)
    return new_account
