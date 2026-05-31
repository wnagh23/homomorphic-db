import time
import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto.encrypt import encrypt, decrypt
from crypto.operations import he_sum, he_mul_plain


class BenchmarkRunner:
    """Mierzy rzeczywisty czas operacji kryptograficznych BFV (Pyfhel).

    Poprzednia wersja używała mock_crypto – wyniki były praktycznie zerowe
    i nie miały wartości edukacyjnej. Ta wersja mierzy prawdziwy narzut HE.
    """

    def __init__(self, record_samples=None):
        self.record_samples = record_samples or [1, 5, 10, 25, 50]
        self.salary_val = 5000

    def measure_encryption(self) -> list[float]:
        """Czas szyfrowania N wartości."""
        times = []
        for n in self.record_samples:
            start = time.perf_counter()
            for _ in range(n):
                encrypt(self.salary_val)
            times.append(time.perf_counter() - start)
        return times

    def measure_he_sum(self) -> list[float]:
        """Czas homomorficznego sumowania N szyfrogramów."""
        times = []
        # Pre-szyfrujemy max liczbę rekordów raz, żeby nie mierzyć encrypt
        max_n = max(self.record_samples)
        ciphertexts = [encrypt(self.salary_val + i * 100) for i in range(max_n)]

        for n in self.record_samples:
            start = time.perf_counter()
            he_sum(ciphertexts[:n])
            times.append(time.perf_counter() - start)
        return times

    def measure_decrypt(self) -> list[float]:
        """Czas deszyfrowania N szyfrogramów."""
        times = []
        max_n = max(self.record_samples)
        ciphertexts = [encrypt(self.salary_val) for _ in range(max_n)]

        for n in self.record_samples:
            start = time.perf_counter()
            for ct in ciphertexts[:n]:
                decrypt(ct)
            times.append(time.perf_counter() - start)
        return times

    def generate_plot(self, enc_times: list[float], sum_times: list[float],
                      dec_times: list[float] = None):
        cols = 3 if dec_times else 2
        fig, axes = plt.subplots(1, cols, figsize=(6 * cols, 5))

        ax1 = axes[0]
        ax1.plot(self.record_samples, enc_times, marker="s", color="#2ca02c", linewidth=2)
        ax1.set_title("Czas szyfrowania (encrypt)", fontsize=12, pad=10)
        ax1.set_xlabel("Liczba rekordów")
        ax1.set_ylabel("Czas [s]")
        ax1.grid(True, linestyle="--", alpha=0.6)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        ax2 = axes[1]
        ax2.plot(self.record_samples, sum_times, marker="o", color="#1f77b4", linewidth=2)
        ax2.set_title("Czas sumowania homomorficznego (he_sum)", fontsize=12, pad=10)
        ax2.set_xlabel("Liczba szyfrogramów")
        ax2.set_ylabel("Czas [s]")
        ax2.grid(True, linestyle="--", alpha=0.6)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        if dec_times:
            ax3 = axes[2]
            ax3.plot(self.record_samples, dec_times, marker="^", color="#d62728", linewidth=2)
            ax3.set_title("Czas deszyfrowania (decrypt)", fontsize=12, pad=10)
            ax3.set_xlabel("Liczba rekordów")
            ax3.set_ylabel("Czas [s]")
            ax3.grid(True, linestyle="--", alpha=0.6)
            ax3.spines["top"].set_visible(False)
            ax3.spines["right"].set_visible(False)

        plt.tight_layout()
        return fig

    def analyze_storage_overhead(self) -> tuple[int, int]:
        """Porównuje rozmiar plaintext vs szyfrogram."""
        plain_size = sys.getsizeof(self.salary_val)
        cipher_bytes = encrypt(self.salary_val)
        cipher_size = len(cipher_bytes)
        return plain_size, cipher_size
