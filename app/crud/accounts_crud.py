from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Account, Transaction
from app.schemas import AccountCreate, AccountUpdate


async def get_accounts_all(db: AsyncSession, user_id: int) -> List[Account]:
    result = await db.execute(select(Account).filter(Account.user_id == user_id))
    accounts = list(result.scalars().all())
    return accounts


async def create_account(db: AsyncSession, user_id: int, account_data: AccountCreate):
    from datetime import datetime

    new_account = Account(
        user_id=user_id,
        bank_code=account_data.bank_code,
        account_number=account_data.account_number,
        account_type=account_data.account_type,
        balance=account_data.balance,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account


async def update_account(
    db: AsyncSession, pk: int, user_id: int, account_data: AccountUpdate
):
    result = await db.execute(
        select(Account).filter(Account.id == pk, Account.user_id == user_id)
    )
    account_to_update = result.scalar_one_or_none()
    if account_to_update:
        account_to_update.bank_code = account_data.bank_code
        account_to_update.account_type = account_data.account_type
        account_to_update.balance = account_data.balance
        await db.commit()
        await db.refresh(account_to_update)
        return account_to_update
    return None


async def delete_account(db: AsyncSession, pk: int, user_id: int):
    result = await db.execute(
        select(Account).filter(Account.id == pk, Account.user_id == user_id)
    )
    account_to_delete = result.scalar_one_or_none()
    if account_to_delete:
        await db.delete(account_to_delete)
        await db.commit()
        return account_to_delete
    return None


# 계좌와 관련된 거래 내역을 조회하는 함수
async def get_account_and_transactions(db: AsyncSession, account_id: int, user_id: int):
    # 계좌 정보 조회
    account_query = select(Account).filter(
        Account.id == account_id, Account.user_id == user_id
    )
    account_result = await db.execute(account_query)
    account = account_result.scalar_one_or_none()

    if account:
        # 계좌와 관련된 거래 내역 조회
        transactions_query = select(Transaction).filter(
            Transaction.account_id == account.id
        )
        transactions_result = await db.execute(transactions_query)
        transactions = transactions_result.scalars().all()

        # 계좌와 거래 내역 반환
        return account, transactions

    return None, []


"""
async def create_user(name: str, email: str, password: str) -> Account:
    async with AsyncSessionLocal() as session:
        new_user = User(name=name, email=email, password=password)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
"""
# AssyncSession + async + await + commit + refresh
