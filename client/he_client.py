import httpx
import base64
import mock_crypto as crypto

def safe_decode(s: str) -> bytes:
    # Умный fallback: если сервер отдал чистый мок-текст, не трогаем Base64
    if s.startswith("HE_CIPHERTEXT"):
        return s.encode('utf-8')
    try:
        # Иначе применяем Base64 с автоматическим выравниванием (padding)
        return base64.b64decode(s + '=' * (-len(s) % 4))
    except Exception:
        return s.encode('utf-8')

class HEClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def add_employee(self, name: str, dept: str, salary: int):
        enc_salary = crypto.encrypt(salary)
        payload = {
            "imie": name,
            "dzial": dept,
            "pensja_enc": base64.b64encode(enc_salary).decode('utf-8')
        }
        response = httpx.post(f"{self.base_url}/records", json=payload)
        response.raise_for_status()
        return response.json()

    def get_employees(self):
        response = httpx.get(f"{self.base_url}/records")
        response.raise_for_status()
        records = response.json()
        
        for r in records:
            # Используем новую безопасную функцию
            enc_bytes = safe_decode(r['pensja_enc'])
            r['pensja_jawna'] = crypto.decrypt(enc_bytes)
        return records

    def get_total_salary(self):
        response = httpx.get(f"{self.base_url}/aggregate/sum")
        response.raise_for_status()
        data = response.json()
        
        # Используем новую безопасную функцию
        enc_bytes = safe_decode(data['wynik_enc'])
        return crypto.decrypt(enc_bytes)

    def raise_salaries(self, percent: int):
        factor = 100 + percent
        response = httpx.post(f"{self.base_url}/transform/raise?factor={factor}")
        response.raise_for_status()
        return response.json()