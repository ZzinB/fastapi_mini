from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import close_async_db, engine  # DB 관련 모듈 가져오기
from app.routes import accounts, analysis, transactions, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to database...")
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)  # 엔진이 준비되었는지 확인
    yield
    print("Closing database connection...")
    await close_async_db()  # 애플리케이션 종료 시 정리


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(analysis.router)


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}


"""
if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
"""
