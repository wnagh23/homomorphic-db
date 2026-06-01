from pydantic import BaseModel


class RecordIn(BaseModel):
    imie: str        # zaszyfrowane Fernetem, base64
    dzial: str       # zaszyfrowane Fernetem, base64
    dzial_token: str
    pensja_enc: str  # zaszyfrowane BFV, base64


class RecordOut(BaseModel):
    id: int
    imie: str        # zaszyfrowane Fernetem, base64
    dzial: str       # zaszyfrowane Fernetem, base64
    pensja_enc: str  # zaszyfrowane BFV, base64


class AggregateResult(BaseModel):
    wynik_enc: str


class CountResult(BaseModel):
    count: int


class RaiseResult(BaseModel):
    zaktualizowano: int
