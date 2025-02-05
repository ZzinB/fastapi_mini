from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import init_db

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 서버 시작: 데이터베이스 초기화")
    init_db()  # 테이블 생성
    yield  # 서버 실행 유지
    print("🛑 서버 종료")

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI with PostgreSQL!","database_url": settings.DATABASE_URL}

