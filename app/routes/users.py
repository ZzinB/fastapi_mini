from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.crud import users_crud
from app.database import get_async_db

router = APIRouter()


# 회원가입
@router.post("/users/signup", response_model=schemas.User)
async def signup_user(
    user: schemas.UserCreate, db: AsyncSession = Depends(get_async_db)
):
    try:
        db_user = await users_crud.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 로그인
@router.post("/users/login")
async def login_user(user: schemas.UserLogin, db: AsyncSession = Depends(get_async_db)):
    return await users_crud.login_user(db, user.email, user.password)


# 로그아웃
@router.post("/users/logout")
async def logout_user(authorization: str = Header(...)):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header is missing")

    token_parts = authorization.split(" ")  # Bearer <token>에서 토큰만 추출
    if len(token_parts) != 2 or token_parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=400, detail="Invalid Authorization header format"
        )

    token = token_parts[1]
    return await users_crud.logout_user(token)


# 사용자 정보 조회
@router.get("/users/info/{user_id}", response_model=schemas.User)
async def get_user_info(user_id: int, db: AsyncSession = Depends(get_async_db)):
    user = await users_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 사용자 정보 수정 (PUT)
@router.put("/users/info/{user_id}", response_model=schemas.User)
async def update_user_info(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    user = await users_crud.update_user(db, user_id, user_update)
    return user


# 사용자 정보 부분 수정 (PATCH)
@router.patch("/users/info/{user_id}", response_model=schemas.User)
async def patch_user_info(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    user = await users_crud.update_user(db, user_id, user_update)
    return user


# 사용자 삭제 (DELETE)
@router.delete("/users/info/{user_id}")
async def delete_user_info(user_id: int, db: AsyncSession = Depends(get_async_db)):
    await users_crud.delete_user(db, user_id)
    return {"message": "User deleted successfully"}
