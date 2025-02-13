from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Analysis
from app.schemas import AnalysisCreate


# 분석 결과 생성
def create_analysis(db: AsyncSession, analysis: AnalysisCreate, user_id: int):
    db_analysis = Analysis(
        user_id=user_id,
        analysis_type=analysis.analysis_type,
        analysis_about=analysis.analysis_about,
        amount=analysis.amount,
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


# 분석 결과 조회 (사용자별)
def get_analyses_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 10
):
    query = (
        select(Analysis).filter(Analysis.user_id == user_id).offset(skip).limit(limit)
    )
    result = db.execute(query)
    return result.scalars().all()
