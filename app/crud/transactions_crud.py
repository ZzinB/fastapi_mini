import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate


# 거래 내역 생성
async def create_transaction(db: AsyncSession, transaction: TransactionCreate):
    db_transaction = Transaction(
        account_id=transaction.account_id,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type,
        transaction_method=transaction.transaction_method,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
    )
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


# 거래 내역 조회
async def get_transactions_all(
    db: AsyncSession,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    transaction_type: Optional[str] = None,
):
    query = select(Transaction)

    if start_date and end_date:
        try:
            start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다. 'YYYY-MM-DD' 형식으로 입력해 주세요.")
        query = query.filter(Transaction.created_at.between(start_dt, end_dt))

    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)

    result = await db.execute(query)
    return result.scalars().all()


# 특정 거래 내역 조회
async def get_transactions(db: AsyncSession, transaction_id: int):
    query = select(Transaction).filter(Transaction.id == transaction_id)
    result = await db.execute(query)
    return result.scalars().first()


# 특정 거래 내역 수정
async def update_transaction(
    db: AsyncSession, transaction_id: int, transaction: TransactionUpdate
):
    query = select(Transaction).filter(Transaction.id == transaction_id)
    result = await db.execute(query)
    db_transaction = result.scalar()
    if db_transaction:
        for key, value in transaction.model_dump(exclude_unset=True).items():
            setattr(db_transaction, key, value)
        await db.commit()
        await db.refresh(db_transaction)
        return db_transaction
    return None


# 특정 거래 내역 삭제
async def delete_transaction(db: AsyncSession, transaction_id: int):
    query = select(Transaction).filter(Transaction.id == transaction_id)
    result = await db.execute(query)
    db_transaction = result.scalar()
    if db_transaction:
        await db.delete(db_transaction)
        await db.commit()
        return db_transaction
    return None
