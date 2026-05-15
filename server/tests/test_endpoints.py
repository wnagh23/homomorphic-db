from fastapi.testclient import TestClient
from server.main import app
from server.db import init_db

client = TestClient(app)

init_db()

def test_add_employee():
    response = client.post("/records", json={
        "imie": "Sebastian Enrique",
        "dzial": "HR",
        "pensja_enc": "fga4123"
    })
    assert response.status_code == 200
    assert response.json()["imie"] == "Sebastian Enrique"


def test_get_records():
    response = client.get("/records")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_single_employee():
    response = client.get("/records/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_nonexistent_employee():
    response = client.get("/records/9999")
    assert response.status_code == 404


def test_delete_employee():
    response = client.delete("/records/1")
    assert response.status_code == 200


def test_delete_nonexistent_employee():
    response = client.delete("/records/9999")
    assert response.status_code == 404