import pytest


# 거래 내역 생성 테스트
@pytest.mark.asyncio
async def test_create_transaction(test_app, test_user: dict):
    token = test_user["token"]

    transaction_data = {
        "account_id": 1,
        "transaction_type": "DEPOSIT",
        "transaction_method": "CARD",
        "amount": 1000.0,
    }

    response = await test_app.post(
        "/transactions",
        json=transaction_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "id" in response.json()  # 생성된 거래 내역의 ID 확인
    assert response.json()["transaction_type"] == transaction_data["transaction_type"]
    assert response.json()["amount"] == transaction_data["amount"]


# 거래 내역 조회 테스트 (전체 조회)
@pytest.mark.asyncio
async def test_get_transactions(test_app, test_user: dict):
    token = test_user["token"]
    # 거래 내역 생성
    transaction_data = {
        "account_id": 1,
        "transaction_type": "DEPOSIT",
        "transaction_method": "CARD",
        "amount": 1000.0,
    }
    response = await test_app.post(
        "/transactions",
        json=transaction_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await test_app.get(
        "/transactions", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)  # 리스트 형태로 거래 내역 응답 확인


# 특정 거래 내역 조회 테스트
@pytest.mark.asyncio
async def test_get_transaction(test_app, test_user: dict):
    token = test_user["token"]

    # 거래 내역 생성
    transaction_data = {
        "account_id": 1,
        "transaction_type": "DEPOSIT",
        "transaction_method": "CARD",
        "amount": 1000.0,
    }
    response = await test_app.post(
        "/transactions",
        json=transaction_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    transaction_id = response.json()["id"]

    # 특정 거래 내역 조회
    response = await test_app.get(
        f"/transactions/{transaction_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id
    assert response.json()["transaction_type"] == transaction_data["transaction_type"]


# 거래 내역 수정 테스트
@pytest.mark.asyncio
async def test_update_transaction(test_app, test_user: dict):
    token = test_user["token"]

    # 거래 내역 생성
    transaction_data = {
        "account_id": 1,
        "transaction_type": "DEPOSIT",
        "transaction_method": "CARD",
        "amount": 1000.0,
    }
    response = await test_app.post(
        "/transactions",
        json=transaction_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    transaction_id = response.json()["id"]

    # 거래 내역 수정
    updated_data = {"amount": 2000.0}

    response = await test_app.put(
        f"/transactions/{transaction_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id
    assert response.json()["amount"] == updated_data["amount"]


# 거래 내역 삭제 테스트
@pytest.mark.asyncio
async def test_delete_transaction(test_app, test_user: dict):
    token = test_user["token"]

    # 거래 내역 생성
    transaction_data = {
        "account_id": 1,
        "transaction_type": "DEPOSIT",
        "transaction_method": "CARD",
        "amount": 1000.0,
    }
    response = await test_app.post(
        "/transactions",
        json=transaction_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    transaction_id = response.json()["id"]

    # 거래 내역 삭제
    response = await test_app.delete(
        f"/transactions/{transaction_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id

    # 삭제된 거래 내역 조회 시 404 오류 발생 확인
    response = await test_app.get(
        f"/transactions/{transaction_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
