from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import models
from app.core.security import (
    blacklist_refresh_token,
    create_access_token,
    hash_password,
    is_token_blacklisted,
    verify_password,
    verify_token,
)
from app.database import get_async_db
from app.models import User
from app.schemas import UserCreate, UserUpdate


# 이메일 중복 체크
async def get_user_by_email(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


# 사용자 생성
async def create_user(db: AsyncSession, user: UserCreate):
    email_str = str(user.email)  # EmailStr을 str로 변환
    # 이메일 중복 확인
    db_user = await get_user_by_email(db, email_str)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # 새로운 사용자 객체 생성
    db_user = User(
        name=user.name,
        email=email_str,
        password=hash_password(user.password),  # 비밀번호는 실제 서비스에서는 해싱이 필요
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)  # 새로 생성된 객체 갱신
        return db_user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the user: {str(e)}",
        )


# 사용자 로그인
async def login_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    user = result.scalars().first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    # JWT 토큰 발급
    access_token_expires = timedelta(minutes=30)  # 액세스 토큰 만료 시간 설정
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 로그아웃 (리프레시 토큰을 블랙리스트에 추가)
async def logout_user(token: str):
    if not token:
        raise HTTPException(status_code=400, detail="Token is missing")
    if is_token_blacklisted(token):
        raise HTTPException(status_code=400, detail="Token is already blacklisted")
    try:
        # JWT 토큰 유효성 검증 (예시)
        jwt.decode(token, "your_secret_key", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token is expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    blacklist_refresh_token(token)
    return {"message": "Successfully logged out"}


# 사용자 정보 수정
async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    # 사용자 찾기
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 이메일이 변경되었는지 확인
    if user_update.email and user_update.email != user.email:
        db_user = await get_user_by_email(db, str(user_update.email))
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )
        user.email = user_update.email

    # 비밀번호 변경이 있으면 해싱하여 저장
    if user_update.password:
        user.password = hash_password(user_update.password)

    # 이름 변경
    if user_update.name:
        user.name = user_update.name

    # DB 커밋
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the user: {str(e)}",
        )


# 사용자 삭제
async def delete_user(db: AsyncSession, user_id: int):
    # 사용자 찾기
    result = await db.execute(select(models.User).filter(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        # 사용자 비활성화 (소프트 삭제)
        user.is_active = False
        user.is_deleted = True
        user.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the user: {str(e)}",
        )


# 사용자 정보 조회
async def get_user(db: AsyncSession, user_id: int):
    # 사용자 조회
    result = await db.execute(
        select(models.User).filter(
            models.User.id == user_id, models.User.is_deleted is False
        )
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)
) -> User:
    try:
        # JWT 토큰에서 사용자 정보 추출
        payload = verify_token(token, algorithms=["HS256"])
        print(f"Payload: {payload}")
        email: str = payload.get("sub")
        print(f"Email: {email}")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # 이메일 기반으로 사용자 찾기
        user = await get_user_by_email(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
