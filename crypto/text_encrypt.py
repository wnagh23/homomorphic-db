from pathlib import Path
from cryptography.fernet import Fernet

BASE_DIR = Path(__file__).resolve().parent
KEYS_DIR = BASE_DIR / "keys"
TEXT_KEY_FILE = KEYS_DIR / "text.key"


def generate_text_key() -> bytes:
    """
    Generuje klucz do szyfrowania pól tekstowych.
    """
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    key = Fernet.generate_key()
    TEXT_KEY_FILE.write_bytes(key)
    return key


def load_text_key() -> bytes:
    """Wczytuje klucz tekstowy albo tworzy go, jeśli jeszcze nie istnieje."""
    if not TEXT_KEY_FILE.exists():
        return generate_text_key()
    return TEXT_KEY_FILE.read_bytes()


def encrypt_text(value: str) -> bytes:
    """Szyfruje tekst i zwraca bajty do zapisania w SQLite jako BLOB."""
    key = load_text_key()
    f = Fernet(key)
    return f.encrypt(value.encode("utf-8"))


def decrypt_text(data: bytes) -> str:
    """Odszyfrowuje tekst. Tej funkcji używa klient, nie serwer."""
    if isinstance(data, memoryview):
        data = data.tobytes()
    if isinstance(data, bytearray):
        data = bytes(data)

    key = load_text_key()
    f = Fernet(key)
    return f.decrypt(data).decode("utf-8")
