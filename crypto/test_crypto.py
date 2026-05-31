"""
Testy jednostkowe modułu kryptograficznego BFV.
Weryfikują poprawność szyfrowania, deszyfrowania i operacji homomorficznych.
"""
from crypto.encrypt import encrypt, decrypt
from crypto.operations import he_sum, he_mul_plain
from crypto.bfv_context import generate_and_save_keys


def setup_module():
    """Generuje świeży kontekst BFV przed uruchomieniem testów."""
    generate_and_save_keys()


def test_encrypt_decrypt():
    """Podstawowa weryfikacja: szyfrowanie i odszyfrowanie tej samej wartości."""
    value = 5000
    assert decrypt(encrypt(value)) == value


def test_encrypt_decrypt_zero():
    assert decrypt(encrypt(0)) == 0


def test_encrypt_decrypt_large():
    """Wartość bliska granicy modułu plaintext (t_bits=22, max ≈ 2_097_152)."""
    value = 1_500_000
    assert decrypt(encrypt(value)) == value


def test_he_sum_two_values():
    """Suma homomorficzna dwóch szyfrogramów."""
    result = he_sum([encrypt(5000), encrypt(7000)])
    assert decrypt(result) == 12000


def test_he_sum_many_values():
    """Suma homomorficzna wielu szyfrogramów."""
    salaries = [3000, 4000, 5000, 6000]
    result = he_sum([encrypt(s) for s in salaries])
    assert decrypt(result) == sum(salaries)


def test_he_sum_single():
    """Suma listy z jednym elementem zwraca ten sam szyfrogram."""
    result = he_sum([encrypt(9999)])
    assert decrypt(result) == 9999


def test_he_mul_plain_double():
    """Mnożenie szyfrogramu przez 2."""
    result = he_mul_plain(encrypt(5000), 2)
    assert decrypt(result) == 10000


def test_he_mul_plain_raise_10_percent():
    """Symulacja podwyżki +10%: factor=110, klient dzieli przez 100.
    5000 * 110 = 550_000 → klient: 550_000 // 100 = 5500."""
    result = he_mul_plain(encrypt(5000), 110)
    raw = decrypt(result)
    assert raw == 550_000
    assert raw // 100 == 5500


def test_he_mul_plain_raise_50_percent():
    """Podwyżka +50%: 4000 * 150 = 600_000 → 6000."""
    result = he_mul_plain(encrypt(4000), 150)
    assert decrypt(result) // 100 == 6000
