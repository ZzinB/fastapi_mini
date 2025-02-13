import pytest


# 계좌 생성 테스트
@pytest.mark.asyncio
async def test_create_account(test_app, test_user: dict):
    user = test_user["user"]
    token = test_user["token"]
    account_data = {
        "bank_code": "001",
        "account_number": "1234567890",
        "account_type": "CHECKING",
        "balance": 1000.0,
    }

    response = await test_app.post(
        "/accounts", json=account_data, headers={"Authorization": f"Bearer {token}"}
    )

    print(response.json())

    assert response.status_code == 200
    assert response.json()["id"] == user.id
    assert response.json()["bank_code"] == account_data["bank_code"]
    assert response.json()["account_number"] == account_data["account_number"]


# 계좌 목록 조회 테스트
@pytest.mark.asyncio
async def test_get_accounts(test_app, test_user: dict):
    token = test_user["token"]
    account_data = {
        "bank_code": "001",
        "account_number": "1234567890",
        "account_type": "CHECKING",
        "balance": 1000.0,
    }

    await test_app.post(
        "/accounts", json=account_data, headers={"Authorization": f"Bearer {token}"}
    )

    response = await test_app.get(
        "/accounts", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)  # 계좌 목록이 리스트 형태인지 확인


# 특정 계좌 목록 조회 테스트
@pytest.mark.asyncio
async def test_get_account(test_app, test_user: dict):
    token = test_user["token"]
    # 계좌 생성
    account_data = {
        "bank_code": "001",
        "account_number": "1234567890",
        "account_type": "CHECKING",
        "balance": 1000.0,
    }

    response = await test_app.post(
        "/accounts", json=account_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    account_id = response.json()["id"]

    # 특정 계좌 조회
    response = await test_app.get(
        f"/accounts/{account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == account_id
    assert response.json()["account_number"].startswith("***-****-")

    transactions = response.json().get("transactions")
    if transactions:
        assert isinstance(transactions, list)
        assert all("id" in transaction for transaction in transactions)
    else:
        # 거래 내역이 없으면 `transactions`가 아예 반환되지 않아야 함
        assert "transactions" not in response.json()


# 계좌 수정 테스트
@pytest.mark.asyncio
async def test_update_account(test_app, test_user: dict):
    token = test_user["token"]
    account_data = {
        "bank_code": "001",
        "account_number": "1234567890",
        "account_type": "CHECKING",
        "balance": 1000.0,
    }

    response = await test_app.post(
        "/accounts", json=account_data, headers={"Authorization": f"Bearer {token}"}
    )

    account_id = response.json()["id"]

    updated_data = {"bank_code": "002", "account_type": "SAVING", "balance": 1500.0}

    response = await test_app.put(
        f"/accounts/{account_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["bank_code"] == updated_data["bank_code"]
    assert response.json()["account_type"] == updated_data["account_type"]
    assert response.json()["balance"] == updated_data["balance"]


# 계좌 삭제 테스트
@pytest.mark.asyncio
async def test_delete_account(test_app, test_user: dict):
    token = test_user["token"]
    account_data = {
        "bank_code": "001",
        "account_number": "1234567890",
        "account_type": "CHECKING",
        "balance": 1000.0,
    }

    response = await test_app.post(
        "/accounts", json=account_data, headers={"Authorization": f"Bearer {token}"}
    )
    account_id = response.json()["id"]

    # 계좌 삭제
    response = await test_app.delete(
        f"/accounts/{account_id}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == account_id
