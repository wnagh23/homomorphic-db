import numpy as np

from crypto.bfv_context import load_client_he
from crypto.serialization import serialize, deserialize


def encrypt(value: int) -> bytes:
    """
    Szyfruje jedną liczbę całkowitą i zwraca bajty szyfrogramu.
    """
    HE = load_client_he()

    value_array = np.array([value], dtype=np.int64)
    ctxt = HE.encryptInt(value_array)

    return serialize(ctxt)


def decrypt(data: bytes) -> int:
    """
    Odszyfrowuje bajty szyfrogramu i zwraca liczbę całkowitą.
    Nie używana po stronie serwera.
    """
    HE = load_client_he()

    ctxt = deserialize(data, HE)
    result = HE.decryptInt(ctxt)

    return int(result[0])