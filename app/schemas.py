from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field

# 은행 코드 및 계좌 종류에 대한 Literal 정의
BANK_CODES = Literal[
    "000",
    "001",
    "002",
    "003",
    "004",
    "005",
    "007",
    "008",
    "011",
    "012",
    "020",
    "023",
    "027",
    "031",
    "032",
    "034",
    "035",
    "037",
    "039",
    "045",
    "048",
    "050",
    "051",
    "052",
    "054",
    "055",
    "056",
    "057",
    "058",
    "059",
    "060",
    "061",
    "062",
    "063",
    "064",
    "065",
    "066",
    "071",
    "076",
    "077",
    "081",
    "088",
    "089",
    "090",
    "092",
    "093",
    "094",
    "095",
    "096",
    "099",
    "102",
    "103",
    "104",
    "105",
    "106",
    "209",
    "218",
    "221",
    "222",
    "223",
    "224",
    "225",
    "226",
    "227",
    "230",
    "238",
    "240",
    "243",
    "261",
    "262",
    "263",
    "264",
    "265",
    "266",
    "267",
    "269",
    "270",
    "278",
    "279",
    "280",
    "287",
    "289",
    "290",
    "291",
    "292",
    "293",
    "294",
    "295",
    "296",
    "297",
    "298",
]

ACCOUNT_TYPE = Literal[
    "CHECKING", "SAVING", "LOAN", "PENSION", "TRUST", "FOREIGN_CURRENCY", "IRP", "STOCK"
]

TRANSACTION_TYPE = Literal["DEPOSIT", "WITHDRAW"]

TRANSACTION_METHOD = Literal[
    "ATM", "TRANSFER", "AUTOMATIC_TRANSFER", "CARD", "INTEREST"
]

ANALYSIS_TYPES = Literal["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]

ANALYSIS_ABOUT = Literal["TOTAL_SPENDING", "TOTAL_INCOME"]


# User 모델 정의
class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None  # None을 허용하여 선택적으로 업데이트
    name: Optional[str] = None
    password: Optional[str] = None  # 비밀번호는 선택적으로 업데이트

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    is_deleted: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    accounts: List["AccountBase"]  # AccountBase로 수정

    class Config:
        orm_mode = True
        use_enum_values = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

    class Config:
        orm_mode = True


# Account 모델 정의
class AccountBase(BaseModel):
    bank_code: BANK_CODES  # Literal로 수정
    account_number: str
    account_type: ACCOUNT_TYPE  # Literal로 수정
    balance: float


class Account(AccountBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        use_enum_values = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    bank_code: BANK_CODES  # Literal로 수정
    account_type: ACCOUNT_TYPE  # Literal로 수정
    balance: float


class AccountDetail(AccountBase):
    transactions: List["TransactionBase"]


# Transaction 모델 정의
class TransactionBase(BaseModel):
    account_id: int
    amount: float
    transaction_type: TRANSACTION_TYPE  # Literal로 수정
    transaction_method: TRANSACTION_METHOD  # Literal로 수정
    created_at: Optional[datetime] = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = datetime.now(timezone.utc)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    transaction_type: Optional[str] = None
    transaction_method: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class Transaction(TransactionBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class AnalysisBase(BaseModel):
    analysis_type: str
    analysis_about: str
    amount: float


class AnalysisCreate(AnalysisBase):
    pass


class Analysis(AnalysisBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
