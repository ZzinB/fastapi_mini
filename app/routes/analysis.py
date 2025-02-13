from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.analysis_crud import create_analysis, get_analyses_by_user
from app.database import get_async_db
from app.schemas import Analysis, AnalysisCreate

router = APIRouter()


# 분석 결과 조회 (사용자별)
@router.get("/analysis", response_model=List[Analysis])
def read_analyses(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_db),
):
    analyses = get_analyses_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return analyses


# 분석 결과 생성
@router.post("/analysis", response_model=Analysis)
def create_new_analysis(
    analysis: AnalysisCreate, user_id: int, db: AsyncSession = Depends(get_async_db)
):
    db_analysis = create_analysis(db, analysis=analysis, user_id=user_id)
    return db_analysis
