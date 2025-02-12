import pytest
from passlib.context import CryptContext

from app.models import User

# 테스트용 사용자 데이터 (DB에 존재한다고 가정)
fake_user_data = {"email": "testuser@example.com", "password": "testpassword"}

# 패스워드 해싱을 위한 CryptContext 객체 생성
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 비밀번호 해싱 함수
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@pytest.mark.asyncio
async def test_login_user(test_app, test_db_session):
    # 테스트용 사용자 등록 (DB에 유저가 존재한다고 가정)
    # 먼저 DB에 테스트용 유저를 삽입
    user_data = {
        "email": fake_user_data["email"],
        "password": fake_user_data["password"],
        "name": "Test User",
    }

    # 비밀번호 해싱
    hashed_password = hash_password(user_data["password"])

    # 해싱된 비밀번호로 사용자 객체 생성
    user = User(
        email=user_data["email"], password=hashed_password, name=user_data["name"]
    )

    # DB에 유저 추가
    test_db_session.add(user)
    await test_db_session.commit()

    # 로그인 요청
    response = await test_app.post(
        "/users/login",
        json={"email": fake_user_data["email"], "password": fake_user_data["password"]},
    )

    # 로그인 성공 여부 확인
    assert response.status_code == 200

    # 응답 상태 코드 확인
    assert response.status_code == 200

    # 응답 내용에서 토큰이 포함되어 있는지 확인
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_logout_user(test_app, test_db_session):
    # 먼저 로그인하여 토큰을 발급받음
    user_data = {
        "email": fake_user_data["email"],
        "password": fake_user_data["password"],
        "name": "Test User",
    }

    hashed_password = hash_password(user_data["password"])

    # DB에 유저 추가 (로그인 전에 미리 존재해야 함)
    user = User(
        email=user_data["email"], password=hashed_password, name=user_data["name"]
    )
    test_db_session.add(user)
    await test_db_session.commit()

    login_response = await test_app.post(
        "/users/login",
        json={"email": fake_user_data["email"], "password": fake_user_data["password"]},
    )

    login_response_data = login_response.json()
    access_token = login_response_data["access_token"]

    # 로그아웃 요청 (Authorization 헤더에 토큰 포함)
    response = await test_app.post(
        "/users/logout", headers={"Authorization": f"Bearer {access_token}"}
    )

    # 응답 상태 코드 확인
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}


@pytest.mark.asyncio
async def test_logout_without_login(test_app):
    # 인증되지 않은 상태에서 로그아웃 시도
    response = await test_app.post(
        "/users/logout", headers={"Authorization": "Bearer invalid_token"}
    )

    # 응답 상태 코드 확인
    assert response.status_code == 401
    assert response.json() == {"detail": "Token is invalid or expired"}
