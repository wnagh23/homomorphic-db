from Pyfhel import PyCtxt

from crypto.bfv_context import load_server_he


def serialize(ctxt: PyCtxt) -> bytes:
    """
    Zamienia szyfrogram Pyfhel na bajty.
    Takie bajty można zapisać w SQLite jako BLOB.
    """
    return ctxt.to_bytes()


def deserialize(data: bytes, HE=None) -> PyCtxt:
    """
    Odtwarza szyfrogram Pyfhel z bajtów.
    HE jest potrzebny, bo szyfrogram musi znać kontekst BFV.
    """
    if HE is None:
        HE = load_server_he()

    if isinstance(data, memoryview):
        data = data.tobytes()

    if isinstance(data, bytearray):
        data = bytes(data)

    return PyCtxt(pyfhel=HE, bytestring=data, scheme="bfv")