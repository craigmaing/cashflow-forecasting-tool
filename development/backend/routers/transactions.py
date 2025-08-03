from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from database.connection import Database
from models.transaction import Transaction
from typing import Optional
from datetime import date

router = APIRouter()

@router.get("/")
async def get_transactions(
    organization_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    transaction_type: Optional[str] = Query(None),
    session: AsyncSession = Depends(Database.get_session)
):
    query = select(Transaction).where(Transaction.organization_id == organization_id)
    
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    
    result = await session.execute(query)
    transactions = result.scalars().all()
    return transactions

@router.post("/")
async def create_transaction(transaction_data: dict, session: AsyncSession = Depends(Database.get_session)):
    new_transaction = Transaction(**transaction_data)
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction
