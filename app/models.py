import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Base Model"""

    pass


class BankCode(enum.Enum):
    알수없음 = "000"
    한국은행 = "001"
    산업은행 = "002"
    기업은행 = "003"
    국민은행 = "004"
    # 필요 시 추가


class AccountType(enum.Enum):
    CHECKING = "입출금"
    SAVING = "적금"
    LOAN = "대출"
    PENSION = "연금"
    TRUST = "신탁"
    FOREIGN_CURRENCY = "외화"
    IRP = "퇴직연금"
    STOCK = "주식"


class TransactionType(enum.Enum):
    DEPOSIT = "입금"
    WITHDRAW = "출금"


class TransactionMethod(enum.Enum):
    ATM = "ATM 거래"
    TRANSFER = "계좌이체"
    AUTOMATIC_TRANSFER = "자동이체"
    CARD = "카드결제"
    INTEREST = "이자"


class AnalysisType(enum.Enum):
    DAILY = "일간"
    WEEKLY = "주간"
    MONTHLY = "월간"
    YEARLY = "연간"


class AnalysisAbout(enum.Enum):
    TOTAL_SPENDING = "총 지출"
    TOTAL_INCOME = "총 수입"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    accounts = relationship("Account", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank_code = Column(Enum(BankCode), nullable=False)
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    balance = Column(Numeric, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    transaction_method = Column(Enum(TransactionMethod), nullable=False)
    amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    account = relationship("Account", back_populates="transactions")


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    analysis_about = Column(Enum(AnalysisAbout), nullable=False)
    amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    user = relationship("User", back_populates="analyses")
