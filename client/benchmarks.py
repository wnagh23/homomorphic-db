import time
import sys
import matplotlib.pyplot as plt
import mock_crypto as crypto

class BenchmarkRunner:
    def __init__(self, record_samples=None):
        self.record_samples = record_samples or [10, 50, 100, 500, 1000]
        self.salary_val = 5000
        
    def measure_encryption(self):
        enc_times = []
        for n in self.record_samples:
            start = time.perf_counter()
            for _ in range(n):
                _ = crypto.encrypt(self.salary_val)
            enc_times.append(time.perf_counter() - start)
        return enc_times

    def measure_he_sum(self):
        sum_times = []
        c1 = crypto.encrypt(100)
        c2 = crypto.encrypt(200)
        for n in self.record_samples:
            start = time.perf_counter()
            for _ in range(n):
                # Symulacja dodawania homomorficznego N razy
                _ = crypto.add_ciphertexts(c1, c2)
            sum_times.append(time.perf_counter() - start)
        return sum_times

    def generate_plot(self, enc_times, sum_times):
        # Tworzymy dwa wykresy obok siebie
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Wykres 1: Szyfrowanie
        ax1.plot(self.record_samples, enc_times, marker='s', color='#2ca02c', linewidth=2)
        ax1.set_title("Czas szyfrowania N rekordów", fontsize=12, pad=10)
        ax1.set_xlabel("Liczba rekordów (N)")
        ax1.set_ylabel("Czas [s]")
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Wykres 2: Suma HE
        ax2.plot(self.record_samples, sum_times, marker='o', color='#1f77b4', linewidth=2)
        ax2.set_title("Czas sumowania homomorficznego (HE Sum)", fontsize=12, pad=10)
        ax2.set_xlabel("Liczba operacji dodawania")
        ax2.set_ylabel("Czas [s]")
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig

    def analyze_storage_overhead(self):
        cipher_bytes = crypto.encrypt(self.salary_val)
        return sys.getsizeof(self.salary_val), sys.getsizeof(cipher_bytes)