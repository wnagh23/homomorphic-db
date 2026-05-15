import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'db.sqlite3'

def get_connection():
    """Otwiera połączenie z bazą i zwraca obiekt conn."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Tworzy tabelę jeśli nie istnieje."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pracownicy (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            imie    TEXT    NOT NULL,
            dzial   TEXT    NOT NULL,
            pensja_enc BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_employee(imie: str, dzial: str, pensja_enc: bytes) -> int:
    """Dodaje pracownika."""
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO pracownicy (imie, dzial, pensja_enc) VALUES (?, ?, ?)",
        (imie, dzial, pensja_enc)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_employees() -> list:
    """Zwraca wszystkich pracowników jako listę słowników."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pracownicy").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_employee(employee_id: int) -> dict | None:
    """Zwraca jednego pracownika lub None jeśli nie istnieje."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM pracownicy WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_employee(employee_id: int) -> bool:
    """Usuwa pracownika. Zwraca True jeśli usunięto, False jeśli nie było."""
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM pracownicy WHERE id = ?", (employee_id,)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def get_all_salaries_enc() -> list[bytes]:
    """Zwraca listę samych szyfrogramów pensji — używane przez agregacje."""
    conn = get_connection()
    rows = conn.execute("SELECT pensja_enc FROM pracownicy").fetchall()
    conn.close()
    return [row["pensja_enc"] for row in rows]


def update_salary_enc(employee_id: int, new_pensja_enc: bytes) -> bool:
    """Nadpisuje szyfrogram pensji"""
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE pracownicy SET pensja_enc = ? WHERE id = ?",
        (new_pensja_enc, employee_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0