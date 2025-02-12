from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 비동기 세션 팩토리
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# 의존성 주입 함수
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


# 애플리케이션 종료 시 엔진 정리
async def close_async_db():
    await engine.dispose()
