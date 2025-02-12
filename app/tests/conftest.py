import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_async_db
from app.main import app
from app.models import Base

# SQLite 메모리 DB URL
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

# 비동기 엔진 및 세션 설정
engine = create_async_engine(TEST_DB_URL, echo=True, future=True)

SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def test_db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # 테이블 생성
    async with SessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # 테이블 삭제


@pytest.fixture(scope="function")
async def test_app(test_db_session) -> AsyncClient:
    """FastAPI 테스트 클라이언트"""
    app.dependency_overrides[get_async_db] = lambda: test_db_session

    # ASGITransport로 app을 감싸서 AsyncClient를 사용
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()  # 테스트 후 초기화
