from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from server.db import (
    init_db,
    add_employee,
    get_all_employees,
    get_employee,
    delete_employee,
    get_all_salaries_enc,
    update_salary_enc,
)
from server.models import RecordIn, RecordOut, CountResult, AggregateResult, RaiseResult
from crypto.operations import he_sum, he_mul_plain
from crypto.transport import b64_to_bytes, bytes_to_b64


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


# ── CRUD ──────────────────────────────────────────────────────────────────────

@app.post("/records", response_model=RecordOut)
def add_record(data: RecordIn):
    """Dodaje nowego pracownika. Pensja trafia do bazy jako szyfrogram – serwer
    nigdy nie widzi wartości w plaintext."""
    pensja_bytes = b64_to_bytes(data.pensja_enc)
    new_id = add_employee(data.imie, data.dzial, pensja_bytes)
    return RecordOut(
        id=new_id,
        imie=data.imie,
        dzial=data.dzial,
        pensja_enc=data.pensja_enc,
    )


@app.get("/records", response_model=list[RecordOut])
def get_records():
    """Zwraca listę wszystkich pracowników. Pensje są zaszyfrowane."""
    employees = get_all_employees()
    result = []
    for emp in employees:
        result.append(RecordOut(
            id=emp["id"],
            imie=emp["imie"],
            dzial=emp["dzial"],
            pensja_enc=bytes_to_b64(emp["pensja_enc"]),
        ))
    return result


@app.get("/records/{employee_id}", response_model=RecordOut)
def get_record(employee_id: int):
    """Zwraca jednego pracownika lub 404."""
    emp = get_employee(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    return RecordOut(
        id=emp["id"],
        imie=emp["imie"],
        dzial=emp["dzial"],
        pensja_enc=bytes_to_b64(emp["pensja_enc"]),
    )


@app.delete("/records/{employee_id}")
def remove_record(employee_id: int):
    """Usuwa pracownika."""
    deleted = delete_employee(employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    return {"message": f"Pracownik {employee_id} usunięty"}


# ── AGREGACJE ─────────────────────────────────────────────────────────────────

@app.get("/aggregate/sum", response_model=AggregateResult)
def aggregate_sum():
    """Suma homomorficzna wszystkich pensji.
    Serwer wykonuje dodawanie BFV na szyfrogramach – nie odszyfrowuje nic."""
    salaries = get_all_salaries_enc()
    if not salaries:
        raise HTTPException(status_code=400, detail="Brak pracowników w bazie")
    wynik_bytes = he_sum(salaries)
    return AggregateResult(wynik_enc=bytes_to_b64(wynik_bytes))


@app.get("/aggregate/count", response_model=CountResult)
def aggregate_count():
    """Liczba pracowników – to jedyna informacja którą serwer zna w plaintext."""
    employees = get_all_employees()
    return CountResult(count=len(employees))


@app.post("/transform/raise", response_model=RaiseResult)
def raise_salaries(factor: int):
    """Mnoży każdą pensję przez jawny współczynnik (np. 110 = +10%).
    To scalar multiplication – serwer zna mnożnik, ale nie zna pensji.
    Klient po odszyfrowaniu dzieli wynik przez 100."""
    employees = get_all_employees()
    if not employees:
        raise HTTPException(status_code=400, detail="Brak pracowników w bazie")

    zaktualizowano = 0
    for emp in employees:
        nowa_pensja_bytes = he_mul_plain(emp["pensja_enc"], factor)
        if update_salary_enc(emp["id"], nowa_pensja_bytes):
            zaktualizowano += 1

    return RaiseResult(zaktualizowano=zaktualizowano)
