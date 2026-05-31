import numpy as np

from crypto.bfv_context import load_server_he
from crypto.serialization import serialize, deserialize


def he_sum(values: list[bytes]) -> bytes:
    """
    Suma homomorficzna wielu zaszyfrowanych liczb.
    """
    if not values:
        raise ValueError("Lista szyfrogramów jest pusta")

    HE = load_server_he()

    result = deserialize(values[0], HE)

    for value in values[1:]:
        ctxt = deserialize(value, HE)
        result += ctxt

    return serialize(result)


def he_mul_plain(ctxt_bytes: bytes, k: int) -> bytes:
    """
    Mnoży szyfrogram przez jawną stałą.
    """
    HE = load_server_he()

    ctxt = deserialize(ctxt_bytes, HE)

    plain_k = HE.encodeInt(np.array([k], dtype=np.int64))
    result = HE.multiply_plain(ctxt, plain_k, in_new_ctxt=True)

    return serialize(result)