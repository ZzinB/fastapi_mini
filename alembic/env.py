import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.models import Base  # SQLAlchemy 모델

# .env 파일 로드
load_dotenv()

# 비동기 SQLAlchemy 엔진 사용
engine = create_async_engine(os.getenv("DATABASE_URL"), echo=True, pool_pre_ping=True)

# 모델의 MetaData 불러오기
target_metadata = Base.metadata


def do_run_migrations(connection):
    """동기 방식으로 마이그레이션 실행"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """온라인 모드에서 마이그레이션 실행"""
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)  # 여기에서 run_sync 사용


def run_migrations_offline() -> None:
    """오프라인 모드에서 마이그레이션 실행"""
    url = os.getenv("DATABASE_URL")  # .env에서 URL을 가져옵니다.
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())  # 비동기 함수 실행
