from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    """Base Model"""

    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)  # 활성화 여부
    is_deleted = Column(Boolean, default=False)  # 삭제 여부
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    accounts = relationship("Account", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    bank_code = Column(String, nullable=False)  # BANK_CODES를 사용할 예정
    account_number = Column(String, unique=True, nullable=False)
    account_type = Column(String, nullable=False)  # ACCOUNT_TYPE을 사용할 예정
    balance = Column(Numeric, default=0)

    is_active = Column(Boolean, default=True)  # 활성화 여부
    is_deleted = Column(Boolean, default=False)  # 삭제 여부
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    transaction_type = Column(String, nullable=False)  # TRANSACTION_TYPE을 사용할 예정
    transaction_method = Column(String, nullable=False)  # TRANSACTION_METHOD을 사용할 예정
    amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    account = relationship("Account", back_populates="transactions")


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    analysis_type = Column(String, nullable=False)  # ANALYSIS_TYPES을 사용할 예정
    analysis_about = Column(String, nullable=False)  # ANALYSIS_ABOUT을 사용할 예정
    amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="analyses")
