from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.transactions_crud import (
    create_transaction,
    delete_transaction,
    get_transactions,
    get_transactions_all,
    update_transaction,
)
from app.database import get_async_db
from app.schemas import Transaction, TransactionCreate, TransactionUpdate

router = APIRouter()


# 모든 거래 내역 조회
@router.get("/transactions", response_model=List[Transaction])
async def get_transactions_view(
    db: AsyncSession = Depends(get_async_db),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
):
    try:
        transactions = await get_transactions_all(
            db, start_date, end_date, transaction_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return transactions


# 거래 내역 생성
@router.post("/transactions", response_model=Transaction)
async def create_transaction_view(
    transaction: TransactionCreate, db: AsyncSession = Depends(get_async_db)
):
    return await create_transaction(db, transaction)


# 특정 거래 내역 조회
@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction_view(
    transaction_id: int, db: AsyncSession = Depends(get_async_db)
):
    transaction = await get_transactions(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


# 거래 내역 수정
@router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction_view(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    updated_transaction = await update_transaction(db, transaction_id, transaction)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction


# 거래 내역 삭제
@router.delete("/transactions/{transaction_id}", response_model=Transaction)
async def delete_transaction_view(
    transaction_id: int, db: AsyncSession = Depends(get_async_db)
):
    deleted_transaction = await delete_transaction(db, transaction_id)
    if not deleted_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return deleted_transaction
