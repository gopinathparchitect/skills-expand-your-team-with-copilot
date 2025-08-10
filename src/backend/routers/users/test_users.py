
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from app import app

client = TestClient(app)

def get_token():
    # For now, use the dummy token from the router
    return "valid-token"

def test_create_user():
    token = get_token()
    response = client.post(
        "/api/users/",
        json={"name": "Alice", "email": "alice@example.com", "role": "student", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "student"
    assert "id" in data

def test_list_users():
    token = get_token()
    response = client.get("/api/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user():
    token = get_token()
    # Create a user first
    create_resp = client.post(
        "/api/users/",
        json={"name": "Bob", "email": "bob@example.com", "role": "teacher", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    user_id = create_resp.json()["id"]
    response = client.get(f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["name"] == "Bob"

def test_update_user():
    token = get_token()
    # Create a user first
    create_resp = client.post(
        "/api/users/",
        json={"name": "Carol", "email": "carol@example.com", "role": "admin", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    user_id = create_resp.json()["id"]
    response = client.put(
        f"/api/users/{user_id}",
        json={"name": "Caroline"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Caroline"

def test_delete_user():
    token = get_token()
    # Create a user first
    create_resp = client.post(
        "/api/users/",
        json={"name": "Dave", "email": "dave@example.com", "role": "admin", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    user_id = create_resp.json()["id"]
    response = client.delete(f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    # Confirm deletion
    get_resp = client.get(f"/api/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 404
