import hashlib
import hmac
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
KEYS_DIR = BASE_DIR / "keys"
INDEX_KEY_FILE = KEYS_DIR / "index.key"


def generate_index_key() -> bytes:
    """
    Generuje klucz do deterministycznych tokenów wyszukiwania.

    Ten klucz powinien być tajny. Bez niego serwer nie powinien sam umieć
    tworzyć tokenów dla zgadywanych wartości, np. "HR" albo "IT".
    """
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    INDEX_KEY_FILE.write_bytes(key)
    return key


def load_index_key() -> bytes:
    """Wczytuje klucz indeksujący albo tworzy go, jeśli nie istnieje."""
    if not INDEX_KEY_FILE.exists():
        return generate_index_key()
    return INDEX_KEY_FILE.read_bytes()


def normalize_text(value: str) -> str:
    """Ujednolica tekst, aby np. ' HR ', 'hr' i 'Hr' miały ten sam token."""
    return value.strip().lower()


def text_token(field_name: str, value: str) -> str:
    """
    Tworzy deterministyczny token HMAC do warunków WHERE.

    field_name rozdziela przestrzenie tokenów, więc token dla imienia "HR"
    będzie inny niż token dla działu "HR".
    """
    key = load_index_key()
    normalized = normalize_text(value)
    message = f"{field_name}:{normalized}".encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()
