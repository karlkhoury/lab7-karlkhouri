import pytest
from flask import json
from app import (app, users, create_db_table, insert_user, get_users,
                 get_user_by_id, update_user, delete_user)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_db_table()


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def new_user():
    return {
        "name": "Test User",
        "email": "testuser@gmail.com",
        "phone": "70111222",
        "address": "Hamra Street, Beirut",
        "country": "Lebanon"
    }


def test_database_created_with_specified_users(tmp_path):
    assert (tmp_path / "database.db").exists()
    db_users = get_users()
    assert len(db_users) == len(users)
    for db_user, user in zip(db_users, users):
        for key in user:
            assert db_user[key] == user[key]


def test_insert_user(new_user):
    inserted = insert_user(new_user)
    assert inserted["user_id"] == len(users) + 1
    for key in new_user:
        assert inserted[key] == new_user[key]
    assert len(get_users()) == len(users) + 1


def test_get_users():
    db_users = get_users()
    assert isinstance(db_users, list)
    assert [u["name"] for u in db_users] == [u["name"] for u in users]
    assert [u["user_id"] for u in db_users] == [1, 2, 3]


def test_get_user_by_id():
    user = get_user_by_id(2)
    assert user["user_id"] == 2
    assert user["name"] == users[1]["name"]
    assert user["email"] == users[1]["email"]
    assert get_user_by_id(999) == {}


def test_update_user():
    user = get_user_by_id(1)
    user["name"] = "John Updated"
    user["country"] = "Germany"
    updated = update_user(user)
    assert updated["name"] == "John Updated"
    assert updated["country"] == "Germany"
    assert get_user_by_id(1)["name"] == "John Updated"


def test_delete_user():
    message = delete_user(1)
    assert message["status"] == "User deleted successfully"
    assert get_user_by_id(1) == {}
    assert len(get_users()) == len(users) - 1


def test_api_get_users(client):
    response = client.get('/api/users')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == len(users)
    assert "Karl Khouri" in str(response.data)


def test_api_get_user(client):
    response = client.get('/api/users/2')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["user_id"] == 2
    for key in users[1]:
        assert data[key] == users[1][key]


def test_api_add_user(client, new_user):
    response = client.post(
        '/api/users/add',
        data=json.dumps(new_user),
        content_type='application/json',
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["user_id"] == len(users) + 1
    for key in new_user:
        assert data[key] == new_user[key]
    assert get_user_by_id(data["user_id"])["email"] == new_user["email"]


def test_api_update_user(client):
    user = get_user_by_id(3)
    user["email"] = "jane.updated@gmail.com"
    user["phone"] = "0447999999"
    response = client.put(
        '/api/users/update',
        data=json.dumps(user),
        content_type='application/json',
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data == user
    assert get_user_by_id(3)["email"] == "jane.updated@gmail.com"


def test_api_delete_user(client):
    response = client.delete('/api/users/delete/3')
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert data["status"] == "User deleted successfully"
    assert get_user_by_id(3) == {}
    assert len(get_users()) == len(users) - 1
