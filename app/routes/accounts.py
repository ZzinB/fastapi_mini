from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.crud import accounts_crud
from app.crud.accounts_crud import get_account_and_transactions
from app.crud.users_crud import get_current_user
from app.database import get_async_db
from app.models import User

router = APIRouter()


# 사용자가 소유한 계좌 목록 조회
@router.get("/accounts", response_model=List[schemas.Account])
async def get_accounts(
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(get_current_user),
):
    accounts = await accounts_crud.get_accounts_all(db=db, user_id=user.id)
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No accounts found for this user",
        )
    return accounts


# 사용자 신규 계좌 생성
@router.post("/accounts", response_model=schemas.Account)
async def create_account(
    account: schemas.AccountCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: models.User = Depends(get_current_user),
):
    print(f"Authenticated user: {current_user}")
    new_account = await accounts_crud.create_account(db, current_user.id, account)
    # 반환 값 없이 처리하고, 성공 시 상태 코드만 반환
    return new_account


# 사용자 특정 계좌 조회
@router.get("/accounts/{pk}", response_model=schemas.AccountDetail)
async def get_account(
    pk: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    account, transactions = await get_account_and_transactions(db, pk, current_user.id)

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Account {pk} not found"
        )

    # 계좌 번호 마스킹 처리
    account.account_number = f"***-****-{account.account_number[-4:]}"

    # 거래 내역 반환
    account.transactions = transactions

    return account


# 사용자 특정 계좌 수정
@router.put("/accounts/{pk}", response_model=schemas.Account)
async def update_account(
    pk: int,
    account: schemas.AccountUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(get_current_user),
):
    updated_account = await accounts_crud.update_account(db, pk, user.id, account)
    if not updated_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Account {pk} not found"
        )
    return updated_account


# 사용자 특정 계좌 삭제
@router.delete("/accounts/{pk}", response_model=schemas.Account)
async def delete_account(
    pk: int,
    db: AsyncSession = Depends(get_async_db),
    user: models.User = Depends(get_current_user),
):
    deleted_account = await accounts_crud.delete_account(db, pk, user.id)
    if not deleted_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Account {pk} not found"
        )
    return deleted_account
