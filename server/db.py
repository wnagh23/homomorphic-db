import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'db.sqlite3'


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pracownicy (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            imie        BLOB    NOT NULL,
            dzial       BLOB    NOT NULL,
            dzial_token TEXT    NOT NULL,
            pensja_enc  BLOB    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_employee(imie: bytes, dzial: bytes, dzial_token: str, pensja_enc: bytes) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO pracownicy (imie, dzial, dzial_token, pensja_enc) VALUES (?, ?, ?, ?)",
        (imie, dzial, dzial_token, pensja_enc)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_employees() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pracownicy").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_employees_by_dept_token(dzial_token: str) -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM pracownicy WHERE dzial_token = ?", (dzial_token,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_employee(employee_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM pracownicy WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_employee(employee_id: int) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM pracownicy WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def get_all_salaries_enc() -> list[bytes]:
    conn = get_connection()
    rows = conn.execute("SELECT pensja_enc FROM pracownicy").fetchall()
    conn.close()
    return [row["pensja_enc"] for row in rows]


def get_salaries_enc_by_token(dzial_token: str) -> list[bytes]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT pensja_enc FROM pracownicy WHERE dzial_token = ?", (dzial_token,)
    ).fetchall()
    conn.close()
    return [row["pensja_enc"] for row in rows]


def update_salary_enc(employee_id: int, new_pensja_enc: bytes) -> bool:
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE pracownicy SET pensja_enc = ? WHERE id = ?",
        (new_pensja_enc, employee_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
