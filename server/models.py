from pydantic import BaseModel

# request models (to co idzie na serwer)

class RecordIn(BaseModel):
    """Dane przy dodawaniu pracownika (POST /records)"""
    imie: str
    dzial: str
    pensja_enc: bytes


class RecordOut(BaseModel):
    """Dane zwracane klientowi"""
    id: int
    imie: str
    dzial: str
    pensja_enc: bytes

class AggregateResult(BaseModel):
    """Wynik agregacji - suma jako bajty"""
    wynik_enc: bytes

class CountResult(BaseModel):
    """Liczba pracownikow"""
    count: int

class RaiseResult(BaseModel):
    """Potwierdzenie po podwyżce"""
    zaktualizowano:int

    