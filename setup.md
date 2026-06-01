# Terminal 1 — serwer
cd ~/paillier-db
uv run uvicorn server.main:app --reload

# Terminal 2 — klient
cd ~/paillier-db/client
uv run streamlit run app.py

# Terminal 3 — SQLite
cd ~/paillier-db
sqlite3 server/db.sqlite3