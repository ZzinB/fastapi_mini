import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 기준으로 .env 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
ENV_PROD_PATH = os.path.join(BASE_DIR, ".env.prod")


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool

    class Config:
        # .env 파일에서 환경 변수를 로드하도록 설정
        env_file = ENV_PATH  # .env 파일 로드
        env_file_encoding = "utf-8"


# 환경 변수 설정 로드
settings = Settings()

# 설정 값 출력 (확인용)
print(settings.DATABASE_URL)
print(settings.DEBUG)
