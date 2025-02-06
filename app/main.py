from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import database  # 비동기 데이터베이스 연결 설정


# 서비스 시작
def start():
    print("service is started.")


# 서비스 종료
def shutdown():
    print("service is stopped.")


# FastAPI lifespan 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서비스 시작 시 데이터베이스 연결
    start()
    await database.connect()  # 비동기 연결

    yield

    # 서비스 종료 시 데이터베이스 연결 끊기
    await database.disconnect()  # 비동기 연결 끊기
    shutdown()


# FastAPI 앱 생성 시 lifespan 사용
app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    from app.core.config import settings

    return {
        "message": "Hello, FastAPI with PostgreSQL!",
        "database_url": settings.DATABASE_URL,
    }
