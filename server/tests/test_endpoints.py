"""
Testy endpointów serwera FastAPI.
Używają prawdziwych szyfrogramów BFV – żadnych mock stringów.
"""
import sys
import os
import base64

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from server.main import app
from server.db import init_db
from crypto.encrypt import encrypt, decrypt
from crypto.transport import bytes_to_b64, b64_to_bytes
from crypto.bfv_context import generate_and_save_keys

client = TestClient(app)


def setup_module():
    """Generuje klucze BFV i inicjalizuje bazę przed testami.
    Czyści tabelę z ewentualnych mock-danych z poprzednich wersji projektu."""
    generate_and_save_keys()
    init_db()
    # Usuń stare rekordy (mogą zawierać mock-stringi zamiast prawdziwych szyfrogramów)
    from server.db import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM pracownicy")
    conn.commit()
    conn.close()


def _enc_b64(value: int) -> str:
    """Helper: szyfruje wartość i zwraca base64."""
    return bytes_to_b64(encrypt(value))


def test_add_employee():
    response = client.post("/records", json={
        "imie": "Anna Nowak",
        "dzial": "IT",
        "pensja_enc": _enc_b64(6000),
    })
    assert response.status_code == 200
    data = response.json()
    assert data["imie"] == "Anna Nowak"
    assert data["dzial"] == "IT"
    # Serwer zwraca szyfrogram jako base64 – nie plaintext
    assert isinstance(data["pensja_enc"], str)
    assert len(data["pensja_enc"]) > 100  # prawdziwy szyfrogram jest duży


def test_get_records():
    response = client.get("/records")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_employee():
    # Dodaj pracownika i pobierz go
    add_resp = client.post("/records", json={
        "imie": "Piotr Wiśniewski",
        "dzial": "HR",
        "pensja_enc": _enc_b64(5500),
    })
    emp_id = add_resp.json()["id"]

    response = client.get(f"/records/{emp_id}")
    assert response.status_code == 200
    assert response.json()["id"] == emp_id


def test_get_nonexistent_employee():
    response = client.get("/records/999999")
    assert response.status_code == 404


def test_delete_employee():
    add_resp = client.post("/records", json={
        "imie": "Do Usunięcia",
        "dzial": "Zarząd",
        "pensja_enc": _enc_b64(3000),
    })
    emp_id = add_resp.json()["id"]

    response = client.delete(f"/records/{emp_id}")
    assert response.status_code == 200

    # Sprawdź że faktycznie zniknął
    get_resp = client.get(f"/records/{emp_id}")
    assert get_resp.status_code == 404


def test_delete_nonexistent_employee():
    response = client.delete("/records/999999")
    assert response.status_code == 404


def test_aggregate_sum_returns_valid_ciphertext():
    """Suma homomorficzna zwraca szyfrogram który można odszyfrować."""
    # Dodaj dwóch pracowników ze znanymi pensjami
    client.post("/records", json={"imie": "X", "dzial": "IT", "pensja_enc": _enc_b64(1000)})
    client.post("/records", json={"imie": "Y", "dzial": "IT", "pensja_enc": _enc_b64(2000)})

    response = client.get("/aggregate/sum")
    assert response.status_code == 200
    data = response.json()
    assert "wynik_enc" in data
    assert isinstance(data["wynik_enc"], str)

    # Klient odszyfrowuje wynik
    result = decrypt(b64_to_bytes(data["wynik_enc"]))
    # Wynik powinien być >= 3000 (mogą być więcej rekordów z poprzednich testów)
    assert result >= 3000


def test_aggregate_count():
    response = client.get("/aggregate/count")
    assert response.status_code == 200
    assert response.json()["count"] >= 0
