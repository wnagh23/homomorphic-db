from pathlib import Path
from Pyfhel import Pyfhel

# Parametry BFV
# n = 2^13 = 8192 — stopień wielomianu (bezpieczeństwo + pojemność)
# t_bits = 22   — rozmiar modułu plaintext
#                 t ≈ 2^22 = 4_194_304, max bezpieczna wartość ≈ 2_097_152
#                 Pozwala przechowywać pensje do ~2 mln PLN oraz wyniki
#                 he_mul_plain(pensja, 150) bez przepełnienia.
# sec = 128     — poziom bezpieczeństwa (128-bitowy)
N = 2 ** 13
T_BITS = 22
SEC = 128

BASE_DIR = Path(__file__).resolve().parent
KEYS_DIR = BASE_DIR / "keys"

CONTEXT_FILE = KEYS_DIR / "context.bin"
PUBLIC_KEY_FILE = KEYS_DIR / "public.key"
SECRET_KEY_FILE = KEYS_DIR / "secret.key"
RELIN_KEY_FILE = KEYS_DIR / "relin.key"


def create_context() -> Pyfhel:
    """Tworzy nowy kontekst BFV i generuje klucze."""
    HE = Pyfhel()
    HE.contextGen(scheme="BFV", n=N, t_bits=T_BITS, sec=SEC)
    HE.keyGen()
    HE.relinKeyGen()
    return HE


def save_context_and_keys(HE: Pyfhel) -> None:
    """Zapisuje kontekst i klucze do plików."""
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    HE.save_context(str(CONTEXT_FILE))
    HE.save_public_key(str(PUBLIC_KEY_FILE))
    HE.save_secret_key(str(SECRET_KEY_FILE))
    HE.save_relin_key(str(RELIN_KEY_FILE))


def keys_exist() -> bool:
    """Sprawdza, czy pliki z kontekstem i kluczami istnieją."""
    return (
        CONTEXT_FILE.exists()
        and PUBLIC_KEY_FILE.exists()
        and SECRET_KEY_FILE.exists()
    )


def generate_and_save_keys() -> Pyfhel:
    """Tworzy nowy kontekst i zapisuje klucze."""
    HE = create_context()
    save_context_and_keys(HE)
    return HE


def load_client_he() -> Pyfhel:
    """Ładuje pełny kontekst klienta (z kluczem prywatnym).
    Klient może szyfrować i odszyfrowywać."""
    if not keys_exist():
        return generate_and_save_keys()

    HE = Pyfhel()
    HE.load_context(str(CONTEXT_FILE))
    HE.load_public_key(str(PUBLIC_KEY_FILE))
    HE.load_secret_key(str(SECRET_KEY_FILE))
    if RELIN_KEY_FILE.exists():
        HE.load_relin_key(str(RELIN_KEY_FILE))
    return HE


def load_server_he() -> Pyfhel:
    """Ładuje kontekst serwera — BEZ klucza prywatnego.
    Serwer może wykonywać operacje homomorficzne, ale nie może odszyfrować."""
    if not CONTEXT_FILE.exists() or not PUBLIC_KEY_FILE.exists():
        generate_and_save_keys()

    HE = Pyfhel()
    HE.load_context(str(CONTEXT_FILE))
    HE.load_public_key(str(PUBLIC_KEY_FILE))
    if RELIN_KEY_FILE.exists():
        HE.load_relin_key(str(RELIN_KEY_FILE))
    return HE
