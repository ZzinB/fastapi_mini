# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# from app.core.config import settings  # 환경 변수 로드
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# # PostgreSQL 데이터베이스 연결 URL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
#
# # 데이터베이스 엔진 생성 (PostgreSQL 설정)
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     pool_pre_ping=True,  # 연결이 끊어진 세션을 감지하고 복구
# )
# 비동기 SQLAlchemy 엔진 사용
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True)

# 세션을 비동기로 사용하도록 설정
AsyncSession = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# # 세션 로컬 생성
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # 베이스 모델 생성
# Base = declarative_base()
#
#
# # 모델과 데이터베이스 테이블을 동기화하는 함수
# def init_db():
#     Base.metadata.create_all(bind=engine)
#
#
# # 데이터베이스 세션 의존성 설정하는 함수
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
