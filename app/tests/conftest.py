from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token
from app.database import get_async_db
from app.main import app
from app.models import Base, User

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


# 공통된 사용자 생성 Fixture
@pytest.fixture(scope="function")
async def test_user(test_db_session) -> User:
    user = User(name="test_user", email="test@example.com", password="testpassword")
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    token = create_access_token(
        data={"email": user.email}, expires_delta=timedelta(minutes=60)
    )
    print(token)
    return {"user": user, "token": token}


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
