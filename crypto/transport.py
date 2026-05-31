import base64


def bytes_to_b64(data: bytes) -> str:
    """Koduje bajty do tekstu base64, żeby można je było przesłać przez JSON."""
    if isinstance(data, memoryview):
        data = data.tobytes()
    if isinstance(data, bytearray):
        data = bytes(data)
    return base64.b64encode(data).decode("ascii")


def b64_to_bytes(data: str) -> bytes:
    """Dekoduje tekst base64 z JSON-a z powrotem do bajtów."""
    return base64.b64decode(data.encode("ascii"))
