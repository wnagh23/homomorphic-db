from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from server.db import (
    init_db,
    add_employee,
    get_all_employees,
    get_employee,
    delete_employee,
    get_all_salaries_enc,
    get_salaries_enc_by_token,
    get_employees_by_dept_token,
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


@app.post("/records", response_model=RecordOut)
def add_record(data: RecordIn):
    imie_bytes = b64_to_bytes(data.imie)
    dzial_bytes = b64_to_bytes(data.dzial)
    pensja_bytes = b64_to_bytes(data.pensja_enc)
    new_id = add_employee(imie_bytes, dzial_bytes, data.dzial_token, pensja_bytes)
    return RecordOut(id=new_id, imie=data.imie, dzial=data.dzial, pensja_enc=data.pensja_enc)


@app.get("/records", response_model=list[RecordOut])
def get_records(dzial_token: str | None = None):
    if dzial_token:
        employees = get_employees_by_dept_token(dzial_token)
    else:
        employees = get_all_employees()
    return [
        RecordOut(
            id=emp["id"],
            imie=bytes_to_b64(emp["imie"]),
            dzial=bytes_to_b64(emp["dzial"]),
            pensja_enc=bytes_to_b64(emp["pensja_enc"]),
        )
        for emp in employees
    ]


@app.get("/records/{employee_id}", response_model=RecordOut)
def get_record(employee_id: int):
    emp = get_employee(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    return RecordOut(
        id=emp["id"], imie=bytes_to_b64(emp["imie"]), dzial=bytes_to_b64(emp["dzial"]),
        pensja_enc=bytes_to_b64(emp["pensja_enc"]),
    )


@app.delete("/records/{employee_id}")
def remove_record(employee_id: int):
    if not delete_employee(employee_id):
        raise HTTPException(status_code=404, detail="Pracownik nie istnieje")
    return {"message": f"Pracownik {employee_id} usunięty"}


@app.get("/aggregate/sum", response_model=AggregateResult)
def aggregate_sum(dzial_token: str | None = None):
    salaries = get_salaries_enc_by_token(dzial_token) if dzial_token else get_all_salaries_enc()
    if not salaries:
        raise HTTPException(status_code=400, detail="Brak pracowników")
    return AggregateResult(wynik_enc=bytes_to_b64(he_sum(salaries)))


@app.get("/aggregate/count", response_model=CountResult)
def aggregate_count(dzial_token: str | None = None):
    if dzial_token:
        employees = get_employees_by_dept_token(dzial_token)
    else:
        employees = get_all_employees()
    return CountResult(count=len(employees))


@app.post("/transform/raise", response_model=RaiseResult)
def raise_salaries(factor: int, dzial_token: str | None = None):
    if dzial_token:
        employees = get_employees_by_dept_token(dzial_token)
    else:
        employees = get_all_employees()
    if not employees:
        raise HTTPException(status_code=400, detail="Brak pracowników")
    zaktualizowano = sum(
        1 for emp in employees
        if update_salary_enc(emp["id"], he_mul_plain(emp["pensja_enc"], factor))
    )
    return RaiseResult(zaktualizowano=zaktualizowano)
