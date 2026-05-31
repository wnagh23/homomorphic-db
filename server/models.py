from pydantic import BaseModel


class RecordIn(BaseModel):
    """Dane przy dodawaniu pracownika (POST /records).
    pensja_enc to szyfrogram zakodowany w base64."""
    imie: str
    dzial: str
    pensja_enc: str   # base64-encoded ciphertext


class RecordOut(BaseModel):
    """Dane zwracane klientowi."""
    id: int
    imie: str
    dzial: str
    pensja_enc: str   # base64-encoded ciphertext


class AggregateResult(BaseModel):
    """Wynik agregacji – zaszyfrowana suma jako base64."""
    wynik_enc: str


class CountResult(BaseModel):
    """Liczba pracowników (plaintext – nie zawiera wartości pensji)."""
    count: int


class RaiseResult(BaseModel):
    """Potwierdzenie po podwyżce."""
    zaktualizowano: int
