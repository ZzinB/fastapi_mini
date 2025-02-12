from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# 사용자 기본 모델 (공통 필드)
class UserBase(BaseModel):
    email: EmailStr  # 이메일 형식 체크
    name: str = Field(..., min_length=3)  # 이름은 최소 3글자 이상
    password: str = Field(..., min_length=6)  # 비밀번호는 최소 6글자 이상


# 사용자 생성 모델 (회원가입 시 필요한 데이터)
class UserCreate(UserBase):
    password: str  # 비밀번호 추가


# 사용자 응답 모델 (DB에 저장된 데이터 반환)
class User(UserBase):
    id: int

    class Config:
        orm_mode = True  # DB 모델과의 변환을 위해 orm_mode 활성화


class UserResponse(BaseModel):
    id: int
    name: str
    email: str


# 로그인 요청
class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True


# 사용자 수정 모델
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=3)
    password: Optional[str] = Field(None, min_length=6)

    class Config:
        orm_mode = True
