import re
import base64

def encrypt(value: int) -> bytes:
    return f"HE_CIPHERTEXT_MOCK_[{value}]".encode('utf-8')

def decrypt(data: bytes) -> int:
    try:
        s = data.decode('utf-8', errors='ignore')
        match = re.search(r'\[(\d+)\]', s)
        if match: 
            return int(match.group(1))
    except Exception:
        pass
    return 0

def add_ciphertexts(c1: bytes, c2: bytes) -> bytes:
    # Tylko na potrzeby benchmarków: symuluje sumę HE
    v1 = decrypt(c1)
    v2 = decrypt(c2)
    return encrypt(v1 + v2)