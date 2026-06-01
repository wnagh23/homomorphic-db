import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from server.main import app
from server.db import init_db, get_connection
from crypto.encrypt import encrypt, decrypt
from crypto.transport import bytes_to_b64, b64_to_bytes
from crypto.bfv_context import generate_and_save_keys
from crypto.text_index import text_token
from crypto.text_encrypt import encrypt_text, decrypt_text

client = TestClient(app)


def setup_module():
    generate_and_save_keys()
    init_db()
    conn = get_connection()
    conn.execute("DELETE FROM pracownicy")
    conn.commit()
    conn.close()


def _payload(name, dept, salary):
    return {
        "imie": bytes_to_b64(encrypt_text(name)),
        "dzial": bytes_to_b64(encrypt_text(dept)),
        "dzial_token": text_token("dzial", dept),
        "pensja_enc": bytes_to_b64(encrypt(salary)),
    }


def test_add_employee():
    r = client.post("/records", json=_payload("Anna Nowak", "IT", 6000))
    assert r.status_code == 200
    assert decrypt_text(b64_to_bytes(r.json()["imie"])) == "Anna Nowak"


def test_get_records():
    r = client.get("/records")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_filter_by_dept():
    client.post("/records", json=_payload("Jan HR", "HR", 4000))
    token = text_token("dzial", "HR")
    r = client.get("/records", params={"dzial_token": token})
    assert r.status_code == 200
    for emp in r.json():
        assert decrypt_text(b64_to_bytes(emp["dzial"])) == "HR"


def test_get_single():
    r = client.post("/records", json=_payload("X", "IT", 5000))
    emp_id = r.json()["id"]
    assert client.get(f"/records/{emp_id}").status_code == 200


def test_get_nonexistent():
    assert client.get("/records/999999").status_code == 404


def test_delete():
    r = client.post("/records", json=_payload("Do usunięcia", "Zarząd", 3000))
    emp_id = r.json()["id"]
    assert client.delete(f"/records/{emp_id}").status_code == 200
    assert client.get(f"/records/{emp_id}").status_code == 404


def test_aggregate_sum():
    r = client.get("/aggregate/sum")
    assert r.status_code == 200
    result = decrypt(b64_to_bytes(r.json()["wynik_enc"]))
    assert result > 0


def test_aggregate_sum_filtered():
    token = text_token("dzial", "HR")
    r = client.get("/aggregate/sum", params={"dzial_token": token})
    assert r.status_code == 200
    result = decrypt(b64_to_bytes(r.json()["wynik_enc"]))
    assert result > 0


def test_aggregate_count():
    r = client.get("/aggregate/count")
    assert r.status_code == 200
    assert r.json()["count"] >= 0


def test_raise_salaries():
    r = client.post("/transform/raise", params={"factor": 110})
    assert r.status_code == 200
    assert r.json()["zaktualizowano"] > 0
