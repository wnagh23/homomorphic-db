import httpx
import sys
import os

# Upewniamy się, że moduł crypto jest dostępny z poziomu client/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.encrypt import encrypt, decrypt
from crypto.transport import bytes_to_b64, b64_to_bytes


class HEClient:
    """Klient bazy danych z szyfrowaniem homomorficznym.

    Klient posiada klucz prywatny i jest jedynym miejscem gdzie dane
    są szyfrowane i odszyfrowywane. Serwer operuje wyłącznie na szyfrogramach.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def add_employee(self, name: str, dept: str, salary: int) -> dict:
        """Szyfruje pensję lokalnie i wysyła szyfrogram na serwer."""
        enc_bytes = encrypt(salary)
        payload = {
            "imie": name,
            "dzial": dept,
            "pensja_enc": bytes_to_b64(enc_bytes),
        }
        response = httpx.post(f"{self.base_url}/records", json=payload)
        response.raise_for_status()
        return response.json()

    def get_employees(self) -> list[dict]:
        """Pobiera pracowników i odszyfrowuje pensje lokalnie."""
        response = httpx.get(f"{self.base_url}/records")
        response.raise_for_status()
        records = response.json()
        for r in records:
            enc_bytes = b64_to_bytes(r["pensja_enc"])
            r["pensja_jawna"] = decrypt(enc_bytes)
        return records

    def get_total_salary(self) -> int:
        """Pobiera zaszyfrowaną sumę z serwera i odszyfrowuje ją lokalnie."""
        response = httpx.get(f"{self.base_url}/aggregate/sum")
        response.raise_for_status()
        data = response.json()
        enc_bytes = b64_to_bytes(data["wynik_enc"])
        return decrypt(enc_bytes)

    def get_count(self) -> int:
        """Pobiera liczbę pracowników."""
        response = httpx.get(f"{self.base_url}/aggregate/count")
        response.raise_for_status()
        return response.json()["count"]

    def raise_salaries(self, percent: int) -> dict:
        """Wysyła podwyżkę jako jawny współczynnik (np. 10% → factor=110).
        Serwer mnoży każdy szyfrogram przez 110 bez wiedzy o wartości pensji.
        Po odczytaniu klient dzieli wynik przez 100."""
        factor = 100 + percent
        response = httpx.post(
            f"{self.base_url}/transform/raise", params={"factor": factor}
        )
        response.raise_for_status()
        return response.json()
