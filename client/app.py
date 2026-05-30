import streamlit as st
import pandas as pd
from he_client import HEClient
from benchmarks import BenchmarkRunner

client = HEClient()
runner = BenchmarkRunner()

st.set_page_config(page_title="Zaszyfrowana Baza HR", layout="wide")
st.title("Bezpieczna Baza Danych HR")
st.write("Demonstracja w pełni homomorficznego szyfrowania (HE).")

tab_add, tab_list, tab_agg, tab_bench = st.tabs([
    "Dodaj pracownika", 
    "Lista pracowników", 
    "Agregacje i Podwyżki", 
    "Wydajność (Benchmarki)"
])

with tab_add:
    st.header("Dodaj nowego pracownika")
    with st.form("add_employee_form"):
        name = st.text_input("Imię i nazwisko")
        dept = st.selectbox("Dział", ["IT", "HR", "Sprzedaż", "Zarząd"])
        salary = st.number_input("Pensja (PLN)", min_value=0, step=100)
        
        submitted = st.form_submit_button("Szyfruj i wyślij do bazy")
        if submitted:
            # WALIDACJA: Blokujemy puste dane
            if not name.strip():
                st.warning("Imię i nazwisko nie może być puste!")
            elif salary <= 0:
                st.warning("Pensja musi być większa niż 0!")
            else:
                try:
                    client.add_employee(name, dept, salary)
                    st.success("Dane zostały pomyślnie zaszyfrowane i zapisane na serwerze.")
                except Exception as e:
                    st.error(f"Wystąpił błąd komunikacji: {e}")
                
    with st.expander("Zobacz co dzieje się w bazie danych (Logi SQL)"):
        st.code("INSERT INTO pracownicy (imie, dzial, pensja_enc) VALUES ('Jan', 'IT', <ZASZYFROWANE_BAJTY>);", language="sql")

with tab_list:
    st.header("Pracownicy w bazie danych")
    if st.button("Odśwież listę"):
        try:
            employees = client.get_employees()
            if employees:
                df = pd.DataFrame(employees)
                display_df = df[['id', 'imie', 'dzial', 'pensja_jawna', 'pensja_enc']]
                display_df.columns = ['ID', 'Imię', 'Dział', 'Pensja Odszyfrowana', 'Zaszyfrowane Bajty (Widok Serwera)']
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("Brak wpisów w bazie danych.")
        except Exception as e:
            st.error(f"Nie udało się pobrać danych: {e}")
            
    with st.expander("Zobacz co dzieje się w bazie danych (Logi SQL)"):
        st.code("SELECT id, imie, dzial, pensja_enc FROM pracownicy;", language="sql")

with tab_agg:
    st.header("Matematyka na zaszyfrowanych danych")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Suma wynagrodzeń")
        if st.button("Oblicz łączny fundusz"):
            try:
                total = client.get_total_salary()
                st.metric(label="Odszyfrowany wynik", value=f"{total} PLN")
            except Exception as e:
                st.error(f"Błąd podczas obliczeń: {e}")
                
        with st.expander("Podgląd operacji backendowych"):
            st.code("SELECT pensja_enc FROM pracownicy;\n-- Następnie: he_sum(szyfrogram1, szyfrogram2)", language="sql")

    with col2:
        st.subheader("Masowa modyfikacja")
        percent = st.slider("Wybierz procent podwyżki", min_value=1, max_value=50, value=10)
        if st.button("Aplikuj podwyżkę dla wszystkich"):
            try:
                result = client.raise_salaries(percent)
                zaktualizowano = result.get('zaktualizowano', 0)
                # WALIDACJA: Jasny komunikat o braku zmian
                if zaktualizowano > 0:
                    st.success(f"Zaktualizowano rekordów: {zaktualizowano}.")
                else:
                    st.warning("Nie zaktualizowano żadnego rekordu. Upewnij się, że baza nie jest pusta.")
            except Exception as e:
                st.error(f"Błąd modyfikacji danych: {e}")
                
        with st.expander("Podgląd operacji backendowych"):
            st.code("UPDATE pracownicy SET pensja_enc = <NOWE_ZASZYFROWANE_BAJTY> WHERE id = ?;", language="sql")

with tab_bench:
    st.header("Analiza wydajności operacji kryptograficznych")
    
    if st.button("Uruchom testy wydajnościowe"):
        with st.spinner("Przetwarzanie tysięcy rekordów..."):
            enc_times = runner.measure_encryption()
            sum_times = runner.measure_he_sum()  # Nowy pomiar
            fig = runner.generate_plot(enc_times, sum_times)
            st.pyplot(fig)
            
            plain_sz, cipher_sz = runner.analyze_storage_overhead()
            
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Rozmiar jawny (1 rekord)", f"{plain_sz} B")
            col_b.metric("Rozmiar szyfrogramu", f"{cipher_sz} B")
            col_c.metric("Narzut pamięciowy", f"~{cipher_sz/plain_sz:.1f}x", delta_color="inverse")