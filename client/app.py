import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from he_client import HEClient, DEPTS
from benchmarks import BenchmarkRunner

client = HEClient()
runner = BenchmarkRunner()

st.set_page_config(page_title="HE Database", layout="wide")
st.title("Silnik bazodanowy — BFV")

tab_add, tab_list, tab_ops, tab_bench = st.tabs([
    "Dodaj pracownika",
    "Lista pracowników",
    "Operacje",
    "Benchmarki",
])

# ── DODAJ ─────────────────────────────────────────────────────────────────────
with tab_add:
    with st.form("form_add"):
        name = st.text_input("Imię i nazwisko")
        dept = st.selectbox("Dział", DEPTS)
        salary = st.number_input("Pensja (PLN)", min_value=1, step=100)
        if st.form_submit_button("Dodaj"):
            if not name.strip():
                st.warning("Podaj imię i nazwisko.")
            else:
                try:
                    client.add_employee(name, dept, int(salary))
                    st.success("Dodano.")
                except Exception as e:
                    st.error(str(e))

# ── LISTA ─────────────────────────────────────────────────────────────────────
with tab_list:
    col_f, col_b = st.columns([3, 1])
    filter_dept = col_f.selectbox("Dział", ["Wszystkie"] + DEPTS, key="filter_list")
    col_b.write("")
    refresh = col_b.button("Odśwież", use_container_width=True)

    try:
        dept_arg = None if filter_dept == "Wszystkie" else filter_dept
        employees = client.get_employees(dept=dept_arg)
        if employees:
            df = pd.DataFrame(employees)[["id", "imie", "dzial", "pensja_jawna", "pensja_enc"]]
            df["pensja_enc"] = df["pensja_enc"].str[:32] + "…"
            df.columns = ["ID", "Imię", "Dział", "Pensja (PLN)", "Szyfrogram"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Brak pracowników.")
    except Exception as e:
        st.error(str(e))

    st.divider()
    col_d1, col_d2 = st.columns([1, 3])
    del_id = col_d1.number_input("ID do usunięcia", min_value=1, step=1, label_visibility="collapsed")
    if col_d2.button("Usuń pracownika"):
        try:
            client.delete_employee(int(del_id))
            st.success(f"Usunięto #{del_id}.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

# ── OPERACJE ──────────────────────────────────────────────────────────────────
with tab_ops:
    dept_ops = st.selectbox("Dział", ["Wszyscy"] + DEPTS, key="filter_ops")
    dept_arg = None if dept_ops == "Wszyscy" else dept_ops
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Suma")
        if st.button("Oblicz", key="btn_sum"):
            try:
                st.metric("PLN", f"{client.get_total_salary(dept=dept_arg):,}".replace(",", " "))
            except Exception as e:
                st.error(str(e))

    with col2:
        st.subheader("Liczba")
        if st.button("Oblicz", key="btn_count"):
            try:
                st.metric("Pracownicy", client.get_count(dept=dept_arg))
            except Exception as e:
                st.error(str(e))

    with col3:
        st.subheader("Średnia")
        if st.button("Oblicz", key="btn_avg"):
            try:
                count = client.get_count(dept=dept_arg)
                if count > 0:
                    avg = client.get_total_salary(dept=dept_arg) // count
                    st.metric("PLN", f"{avg:,}".replace(",", " "))
                else:
                    st.warning("Brak danych.")
            except Exception as e:
                st.error(str(e))

    st.divider()
    st.subheader("Podwyżka")
    col_s, col_b2 = st.columns([3, 1])
    percent = col_s.slider("Procent", min_value=1, max_value=50, value=10, label_visibility="collapsed")
    col_b2.write("")
    if col_b2.button(f"+{percent}%", use_container_width=True):
        try:
            n = client.raise_salaries(percent, dept=dept_arg).get("zaktualizowano", 0)
            st.success(f"Zaktualizowano {n} rekordów.")
        except Exception as e:
            st.error(str(e))

# ── BENCHMARKI ────────────────────────────────────────────────────────────────
with tab_bench:
    if st.button("Uruchom benchmarki"):
        with st.spinner("Trwa pomiar…"):
            try:
                fig = runner.generate_plot(
                    runner.measure_encryption(),
                    runner.measure_he_sum(),
                    runner.measure_decrypt(),
                )
                st.pyplot(fig)

                plain_sz, cipher_sz = runner.analyze_storage_overhead()
                c1, c2, c3 = st.columns(3)
                c1.metric("int (plaintext)", f"{plain_sz} B")
                c2.metric("Szyfrogram BFV", f"{cipher_sz:,} B".replace(",", " "))
                c3.metric("Narzut pamięciowy", f"~{cipher_sz // plain_sz}×")
            except Exception as e:
                st.error(str(e))
