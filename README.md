# paillier-db

Silnik bazodanowy z szyfrowaniem homomorficznym — Temat 7.

Schemat **BFV** (Brakerski-Fan-Vercauteren) zaimplementowany przez bibliotekę
**Pyfhel** (wrapper na Microsoft SEAL).

## Architektura

```
┌─────────────────────────────────────────────────────────┐
│  KLIENT (posiada klucz prywatny)                        │
│  • szyfruje pensje przed wysłaniem                      │
│  • odszyfrowuje wyniki agregacji                        │
└────────────────────┬──────────────────┬─────────────────┘
                     │  szyfrogram      │  szyfrogram
                     ▼                  ▲
┌─────────────────────────────────────────────────────────┐
│  SERWER (nie ma klucza prywatnego)                      │
│  • przechowuje szyfrogramy w SQLite (BLOB)              │
│  • wykonuje he_sum / he_mul_plain na szyfrogramach BFV  │
│  • nigdy nie widzi wartości pensji w plaintext          │
└─────────────────────────────────────────────────────────┘
```

## Struktura projektu

```
paillier-db/
├── crypto/              # Warstwa kryptograficzna (Pyfhel/BFV)
│   ├── bfv_context.py   # Generowanie i ładowanie kluczy BFV
│   ├── encrypt.py       # Encrypt / Decrypt (tylko klient)
│   ├── operations.py    # he_sum, he_mul_plain (serwer, bez klucza prywatnego)
│   ├── serialization.py # PyCtxt ↔ bytes (BLOB do SQLite)
│   ├── transport.py     # bytes ↔ base64 (JSON przez HTTP)
│   ├── text_encrypt.py  # Szyfrowanie pól tekstowych (Fernet)
│   ├── text_index.py    # HMAC tokeny do WHERE na tekście
│   └── test_crypto.py   # Testy jednostkowe kryptografii
├── server/
│   ├── main.py          # FastAPI: endpointy CRUD + agregacje
│   ├── db.py            # SQLite: CRUD na tabeli pracownicy
│   ├── models.py        # Modele Pydantic
│   └── tests/
│       └── test_endpoints.py
├── client/
│   ├── app.py           # Interfejs Streamlit
│   ├── he_client.py     # HTTP klient (szyfruje/odszyfrowuje lokalnie)
│   └── benchmarks.py    # Pomiary wydajności BFV
└── pyproject.toml
```

## Uruchomienie

### 1. Instalacja zależności

```bash
pip install -e .
# lub z uv:
uv sync
```

Pyfhel wymaga kompilatora C++ (gcc/clang). Na Ubuntu: `apt install build-essential`.

### 2. Generowanie kluczy BFV

Klucze są generowane automatycznie przy pierwszym uruchomieniu serwera.
Można też wygenerować ręcznie:

```bash
cd paillier-db
python -c "from crypto.bfv_context import generate_and_save_keys; generate_and_save_keys(); print('OK')"
```

Klucze trafiają do `crypto/keys/`. Folder jest w `.gitignore` — nie commituj kluczy.

### 3. Serwer FastAPI

```bash
cd paillier-db
uvicorn server.main:app --reload
# API dostępne na http://localhost:8000
# Dokumentacja: http://localhost:8000/docs
```

### 4. Klient Streamlit

W osobnym terminalu:

```bash
cd paillier-db/client
streamlit run app.py
```

### 5. Testy

```bash
cd paillier-db
pytest crypto/test_crypto.py -v          # testy kryptografii
pytest server/tests/test_endpoints.py -v # testy endpointów
```

## Obsługiwane operacje

| Operacja | Endpoint | Opis |
|---|---|---|
| Dodaj pracownika | `POST /records` | Klient szyfruje pensję, serwer zapisuje BLOB |
| Lista pracowników | `GET /records` | Serwer zwraca szyfrogramy, klient odszyfrowuje |
| Suma pensji | `GET /aggregate/sum` | `he_sum` na szyfrogramach BFV |
| Liczba pracowników | `GET /aggregate/count` | Jedyna operacja na plaintext |
| Podwyżka | `POST /transform/raise?factor=110` | `he_mul_plain` — serwer mnoży szyfrogramy przez stałą |

## Uwagi techniczne

**Noise budget**: każde mnożenie ciphertext×ciphertext zużywa budżet szumu.
Przy `n=2^13, t_bits=20` bezpieczna głębokość to ~3-4 mnożenia.
Operacje addytywne (`he_sum`) nie zużywają budżetu.

**Narzut pamięciowy**: szyfrogram BFV dla jednej liczby int ≈ 7 KB (vs 8 B plaintext → ~1000×).
To typowy koszt schematów RLWE — wynika z konieczności ukrycia struktury algebraicznej.

**WHERE na zaszyfrowanych danych**: porównanie `Enc(x) == Enc(y)` bez klucza jest niemożliwe
w BFV. Moduł `text_index.py` implementuje obejście przez tokeny HMAC dla równości tekstowej.
