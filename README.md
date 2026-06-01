# homomorphic-db

Silnik bazodanowy z szyfrowaniem homomorficznym (schemat BFV, Pyfhel/Microsoft SEAL).

Serwer przechowuje i przetwarza dane pracowników nie widząc żadnej wartości w plaintext. Klucz prywatny istnieje wyłącznie po stronie klienta.

**Autorzy:** Wojciech Niemiec, Emilia Stachnik, Ivan Polischuk

## Architektura

```
KLIENT (klucz prywatny) — szyfruje przed wysłaniem, odszyfrowuje wyniki
         ↕ JSON/HTTP (base64)
SERWER (bez klucza) — przechowuje BLOBy w SQLite, wykonuje he_sum / he_mul_plain
```

## Uruchomienie

```bash
uv sync                                      # instalacja zależności
uvicorn server.main:app --reload             # serwer → http://localhost:8000
cd client && streamlit run app.py            # klient → http://localhost:8501
```

Pyfhel wymaga kompilatora C++. Ubuntu: `apt install build-essential`.  
Klucze BFV generują się automatycznie przy pierwszym starcie serwera.

## API

| Endpoint | Opis |
|---|---|
| `POST /records` | Dodaj pracownika (zaszyfrowane dane) |
| `GET /records` | Lista; filtr `?dzial_token=<hex>` |
| `DELETE /records/{id}` | Usuń pracownika |
| `GET /aggregate/sum` | Suma pensji (wynik jako szyfrogram) |
| `GET /aggregate/count` | Liczba pracowników |
| `POST /transform/raise?factor=110` | Podwyżka +10% na szyfrogramach |

## Testy

```bash
pytest -v
```

