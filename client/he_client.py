import httpx
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.encrypt import encrypt, decrypt
from crypto.transport import bytes_to_b64, b64_to_bytes
from crypto.text_index import text_token
from crypto.text_encrypt import encrypt_text, decrypt_text

DEPTS = ["IT", "HR", "Sprzedaż", "Zarząd"]


class HEClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def add_employee(self, name: str, dept: str, salary: int) -> dict:
        payload = {
            "imie": bytes_to_b64(encrypt_text(name)),
            "dzial": bytes_to_b64(encrypt_text(dept)),
            "dzial_token": text_token("dzial", dept),
            "pensja_enc": bytes_to_b64(encrypt(salary)),
        }
        r = httpx.post(f"{self.base_url}/records", json=payload)
        r.raise_for_status()
        return r.json()

    def get_employees(self, dept: str | None = None) -> list[dict]:
        params = {}
        if dept:
            params["dzial_token"] = text_token("dzial", dept)
        r = httpx.get(f"{self.base_url}/records", params=params)
        r.raise_for_status()
        records = r.json()
        for rec in records:
            rec["imie"] = decrypt_text(b64_to_bytes(rec["imie"]))
            rec["dzial"] = decrypt_text(b64_to_bytes(rec["dzial"]))
            rec["pensja_jawna"] = decrypt(b64_to_bytes(rec["pensja_enc"]))
        return records

    def delete_employee(self, employee_id: int) -> dict:
        r = httpx.delete(f"{self.base_url}/records/{employee_id}")
        r.raise_for_status()
        return r.json()

    def get_total_salary(self, dept: str | None = None) -> int:
        params = {}
        if dept:
            params["dzial_token"] = text_token("dzial", dept)
        r = httpx.get(f"{self.base_url}/aggregate/sum", params=params)
        r.raise_for_status()
        return decrypt(b64_to_bytes(r.json()["wynik_enc"]))

    def get_count(self, dept: str | None = None) -> int:
        params = {}
        if dept:
            params["dzial_token"] = text_token("dzial", dept)
        r = httpx.get(f"{self.base_url}/aggregate/count", params=params)
        r.raise_for_status()
        return r.json()["count"]

    def raise_salaries(self, percent: int, dept: str | None = None) -> dict:
        params = {"factor": 100 + percent}
        if dept:
            params["dzial_token"] = text_token("dzial", dept)
        r = httpx.post(f"{self.base_url}/transform/raise", params=params)
        r.raise_for_status()
        return r.json()
