from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from server.db import init_db, add_employee, get_all_employees, get_employee, delete_employee
from server.models import RecordIn, RecordOut, CountResult

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)


# endpointy crud
# Dodałem te dwie funkcję aby mock działał w tym czasi, w przyszłości 
# najprawdopodobniej do usunięcia

import re
import base64

def he_sum(salaries: list[bytes]) -> bytes:
    suma = 0
    for s in salaries:
        try:
            s_str = s.decode('utf-8', errors='ignore')
            # Если данные в БД лежат в Base64, расшифровываем их
            if not s_str.startswith("HE_CIPHERTEXT"):
                try:
                    s_str = base64.b64decode(s_str).decode('utf-8')
                except Exception:
                    pass
            
            match = re.search(r'\[(\d+)\]', s_str)
            if match:
                suma += int(match.group(1))
        except Exception:
            continue
    return f"HE_CIPHERTEXT_MOCK_[{suma}]".encode('utf-8')

def he_mul_plain(salary_enc: bytes, factor: int) -> bytes:
    try:
        s_str = salary_enc.decode('utf-8', errors='ignore')
        # Снова проверка на Base64 для операций умножения
        if not s_str.startswith("HE_CIPHERTEXT"):
            try:
                s_str = base64.b64decode(s_str).decode('utf-8')
            except Exception:
                pass
            
        match = re.search(r'\[(\d+)\]', s_str)
        if match:
            nowa_wartosc = int((int(match.group(1)) * factor) / 100)
            return f"HE_CIPHERTEXT_MOCK_[{nowa_wartosc}]".encode('utf-8')
    except Exception:
        pass
    return salary_enc

@app.post("/records", response_model=RecordOut)
def add_record(data: RecordIn):
    """Dodaje nowego pracownika."""
    new_id = add_employee(data.imie, data.dzial, data.pensja_enc)
    return RecordOut(
        id=new_id,
        imie=data.imie,
        dzial=data.dzial,
        pensja_enc=data.pensja_enc
    )


@app.get("/records", response_model=list[RecordOut])
def get_records():
    """Zwraca listę wszystkich pracowników."""
    return get_all_employees()


@app.get("/records/{employee_id}", response_model=RecordOut)
def get_record(employee_id: int):
    """Zwraca jednego pracownika."""
    employee = get_employee(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    return employee


@app.delete("/records/{employee_id}")
def remove_record(employee_id: int):
    """Usuwa pracownika."""
    deleted = delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    return {"message": f"Pracownik {employee_id} usunięty"}


# endpointy agregacyjne

from server.db import get_all_salaries_enc, get_all_employees, update_salary_enc
from server.models import AggregateResult, CountResult, RaiseResult


#from crypto.operations import he_sum, he_mul_plain


@app.get("/aggregate/sum", response_model=AggregateResult)
def aggregate_sum():
    """Suma homomorficzna wszystkich pensji"""
    salaries = get_all_salaries_enc()
    if not salaries:
        raise HTTPException(status_code=400, detail="Brak pracowników w bazie")
    wynik = he_sum(salaries)  # Kryptograf dostarcza tę funkcję
    return AggregateResult(wynik_enc=wynik)


@app.get("/aggregate/count", response_model=CountResult)
def aggregate_count():
    """Liczba pracowników"""
    employees = get_all_employees()
    return CountResult(count=len(employees))


@app.post("/transform/raise", response_model=RaiseResult)
def raise_salaries(factor: int):
    """Mnoży każdą pensję przez factor"""
    employees = get_all_employees()
    if not employees:
        raise HTTPException(status_code=400, detail="Brak pracowników w bazie")

    zaktualizowano = 0
    for emp in employees:
        nowa_pensja = he_mul_plain(emp["pensja_enc"], factor)
        updated = update_salary_enc(emp["id"], nowa_pensja)
        if updated:
            zaktualizowano += 1

    return RaiseResult(zaktualizowano=zaktualizowano)