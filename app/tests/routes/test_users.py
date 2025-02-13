import pytest
from sqlalchemy.future import select

from app.models import User


@pytest.mark.asyncio
async def test_signup_user(test_app, test_db_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "password",
    }

    # 비동기 요청을 통해 API 호출
    response = await test_app.post("/users/signup", json=user_data)

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["email"] == user_data["email"]
    assert response_data["name"] == user_data["name"]

    # DB에서 해당 사용자 확인
    # `select`를 사용하여 User 객체를 쿼리합니다.
    result = await test_db_session.execute(
        select(User).filter(User.email == user_data["email"])
    )
    user = (
        result.scalar_one_or_none()
    )  # 결과가 하나일 경우, None도 반환될 수 있으므로 `scalar_one_or_none`을 사용
    assert user is not None
    assert user.name == user_data["name"]
    assert user.email == user_data["email"]


# 사용자 정보 조회
@pytest.mark.asyncio
async def test_get_user_info(test_app, test_db_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "password",
    }

    # 사용자 생성
    signup_response = await test_app.post("/users/signup", json=user_data)
    user_id = signup_response.json()["id"]

    # 사용자 정보 조회
    response = await test_app.get(f"/users/info/{user_id}")

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == user_data["name"]
    assert response_data["email"] == user_data["email"]


# 사용자 정보 수정
@pytest.mark.asyncio
async def test_update_user_info(test_app, test_db_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "password",
    }

    # 사용자 생성
    signup_response = await test_app.post("/users/signup", json=user_data)
    user_id = signup_response.json()["id"]

    # 수정할 데이터
    update_data = {
        "name": "updated_user",
        "email": "updateduser@example.com",
        "password": "newpassword",
    }

    # 사용자 정보 수정 요청
    response = await test_app.put(f"/users/info/{user_id}", json=update_data)

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == update_data["name"]
    assert response_data["email"] == update_data["email"]

    # DB에서 변경 확인
    result = await test_db_session.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.name == update_data["name"]
    assert user.email == update_data["email"]


# 사용자 정보 부분 수정
@pytest.mark.asyncio
async def test_patch_user_info(test_app, test_db_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "password",
    }

    # 사용자 생성
    signup_response = await test_app.post("/users/signup", json=user_data)
    user_id = signup_response.json()["id"]

    # 수정할 데이터 (부분 업데이트)
    patch_data = {"name": "patched_user"}

    # 사용자 정보 부분 수정 요청
    response = await test_app.patch(f"/users/info/{user_id}", json=patch_data)

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == patch_data["name"]

    # DB에서 변경 확인
    result = await test_db_session.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.name == patch_data["name"]


# 사용자 삭제
@pytest.mark.asyncio
async def test_delete_user_info(test_app, test_db_session):
    user_data = {
        "name": "testuser",
        "email": "testuser@example.com",
        "password": "password",
    }

    # 사용자 생성
    signup_response = await test_app.post("/users/signup", json=user_data)
    user_id = signup_response.json()["id"]

    # 사용자 삭제 요청
    response = await test_app.delete(f"/users/info/{user_id}")

    # 응답 검증
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "User deleted successfully"

    # DB에서 삭제 확인
    result = await test_db_session.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    # 사용자 정보가 DB에 남아 있는지 확인
    assert user is not None
    assert user.is_deleted is True  # is_deleted가 True로 설정되어 있어야 함
    assert user.deleted_at is not None  # deleted_at 필드가 None이 아니어야 함

    # 실제 삭제된 경우는 아닌지 확인
    assert user.is_active is False  # 사용자가 비활성화되었어야 함
