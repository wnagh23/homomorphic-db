from pydantic import BaseModel


class RecordIn(BaseModel):
    imie: str
    dzial: str
    dzial_token: str
    pensja_enc: str


class RecordOut(BaseModel):
    id: int
    imie: str
    dzial: str
    pensja_enc: str


class AggregateResult(BaseModel):
    wynik_enc: str


class CountResult(BaseModel):
    count: int


class RaiseResult(BaseModel):
    zaktualizowano: int
