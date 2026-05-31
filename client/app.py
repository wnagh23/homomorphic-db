import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from he_client import HEClient
from benchmarks import BenchmarkRunner

client = HEClient()
runner = BenchmarkRunner()

st.set_page_config(page_title="Zaszyfrowana Baza HR", layout="wide")
st.title("Silnik bazodanowy z szyfrowaniem homomorficznym")
st.caption(
    "Schemat BFV (Pyfhel / Microsoft SEAL). "
    "Serwer wykonuje obliczenia na szyfrogramach – nie zna wartości pensji."
)

tab_add, tab_list, tab_agg, tab_bench = st.tabs([
    "➕ Dodaj pracownika",
    "👥 Lista pracowników",
    "∑ Agregacje i podwyżki",
    "⏱ Benchmarki",
])

# ── DODAJ PRACOWNIKA ──────────────────────────────────────────────────────────
with tab_add:
    st.header("Dodaj nowego pracownika")
    with st.form("add_employee_form"):
        name = st.text_input("Imię i nazwisko")
        dept = st.selectbox("Dział", ["IT", "HR", "Sprzedaż", "Zarząd"])
        salary = st.number_input("Pensja (PLN)", min_value=0, step=100)
        submitted = st.form_submit_button("Szyfruj i wyślij do bazy")

        if submitted:
            if not name.strip():
                st.warning("Imię i nazwisko nie może być puste.")
            elif salary <= 0:
                st.warning("Pensja musi być większa niż 0.")
            else:
                try:
                    client.add_employee(name, dept, int(salary))
                    st.success(
                        f"Dane zapisane. Serwer przechowuje szyfrogram – "
                        f"nie zna wartości {int(salary)} PLN."
                    )
                except Exception as e:
                    st.error(f"Błąd komunikacji z serwerem: {e}")

    with st.expander("Co trafia do bazy danych?"):
        st.code(
            "INSERT INTO pracownicy (imie, dzial, pensja_enc)\n"
            "VALUES ('Jan Kowalski', 'IT', <BLOB: szyfrogram BFV ~7 KB>);",
            language="sql",
        )

# ── LISTA PRACOWNIKÓW ─────────────────────────────────────────────────────────
with tab_list:
    st.header("Pracownicy w bazie danych")
    if st.button("Odśwież listę"):
        try:
            employees = client.get_employees()
            if employees:
                df = pd.DataFrame(employees)
                display_df = df[["id", "imie", "dzial", "pensja_jawna", "pensja_enc"]].copy()
                display_df["pensja_enc"] = display_df["pensja_enc"].str[:40] + "…"
                display_df.columns = [
                    "ID", "Imię", "Dział",
                    "Pensja (odszyfrowana przez klienta)",
                    "Szyfrogram (widok serwera, pierwsze 40 znaków base64)",
                ]
                st.dataframe(display_df, use_container_width=True)
                st.info(
                    "Kolumna 'Szyfrogram' to fragment tego co widzi serwer – "
                    "ciąg bajtów bez żadnej informacji o wartości pensji."
                )
            else:
                st.info("Baza jest pusta. Dodaj pracowników w pierwszej zakładce.")
        except Exception as e:
            st.error(f"Nie udało się pobrać danych: {e}")

    with st.expander("Zapytanie SQL po stronie serwera"):
        st.code("SELECT id, imie, dzial, pensja_enc FROM pracownicy;", language="sql")

# ── AGREGACJE ─────────────────────────────────────────────────────────────────
with tab_agg:
    st.header("Operacje homomorficzne na zaszyfrowanych danych")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Suma wynagrodzeń (HE SUM)")
        st.caption(
            "Serwer dodaje szyfrogramy operatorem BFV. "
            "Klient odszyfrowuje wynik."
        )
        if st.button("Oblicz łączny fundusz płac"):
            try:
                total = client.get_total_salary()
                st.metric("Odszyfrowany wynik", f"{total:,} PLN".replace(",", " "))
            except Exception as e:
                st.error(f"Błąd: {e}")

        with st.expander("Co robi serwer?"):
            st.code(
                "# server/main.py\n"
                "salaries = get_all_salaries_enc()   # lista BLOB-ów\n"
                "wynik = he_sum(salaries)            # BFV add na szyfrogramach\n"
                "# wynik to nadal szyfrogram – serwer nie zna sumy",
                language="python",
            )

    with col2:
        st.subheader("Masowa podwyżka (HE MUL PLAIN)")
        st.caption(
            "Serwer mnoży każdy szyfrogram przez jawny współczynnik. "
            "Nie zna wartości pensji – zna tylko procent podwyżki."
        )
        percent = st.slider("Procent podwyżki", min_value=1, max_value=50, value=10)
        st.write(f"Współczynnik wysyłany do serwera: **{100 + percent}**")

        if st.button("Aplikuj podwyżkę"):
            try:
                result = client.raise_salaries(percent)
                n = result.get("zaktualizowano", 0)
                if n > 0:
                    st.success(
                        f"Zaktualizowano {n} rekordów. "
                        f"Każda pensja została pomnożona przez {100+percent}, "
                        f"klient dzieli wynik przez 100 przy odszyfrowaniu."
                    )
                else:
                    st.warning("Brak rekordów do zaktualizowania.")
            except Exception as e:
                st.error(f"Błąd: {e}")

        with st.expander("Co robi serwer?"):
            st.code(
                "# server/main.py\n"
                "for emp in employees:\n"
                "    nowa = he_mul_plain(emp['pensja_enc'], factor)  # BFV scalar mul\n"
                "    update_salary_enc(emp['id'], nowa)\n"
                "# serwer zna tylko 'factor', nie zna żadnej pensji",
                language="python",
            )

# ── BENCHMARKI ────────────────────────────────────────────────────────────────
with tab_bench:
    st.header("Analiza wydajności operacji BFV")
    st.info(
        "Benchmarki mierzą rzeczywisty czas Pyfhel/SEAL – nie mock. "
        "Spodziewany narzut HE vs plaintext: 100×–1000×."
    )

    if st.button("Uruchom benchmarki"):
        with st.spinner("Wykonywanie operacji kryptograficznych BFV…"):
            try:
                enc_times = runner.measure_encryption()
                sum_times = runner.measure_he_sum()
                dec_times = runner.measure_decrypt()
                fig = runner.generate_plot(enc_times, sum_times, dec_times)
                st.pyplot(fig)

                plain_sz, cipher_sz = runner.analyze_storage_overhead()
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Rozmiar int (plaintext)", f"{plain_sz} B")
                col_b.metric("Rozmiar szyfrogramu BFV", f"{cipher_sz:,} B".replace(",", " "))
                col_c.metric(
                    "Narzut pamięciowy",
                    f"~{cipher_sz / plain_sz:.0f}×",
                    delta_color="inverse",
                )
                st.caption(
                    "Narzut pamięciowy ~1000× jest typowy dla schematów RLWE (BFV/CKKS). "
                    "To cena prywatności – szyfrogram musi ukrywać strukturę algebraiczną plaintext."
                )
            except Exception as e:
                st.error(f"Błąd podczas benchmarków: {e}")
