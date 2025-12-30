# debug_db_check.py
from database import engine
from sqlalchemy import text

def run():
    with engine.connect() as conn:
        print("DB_NAME:", conn.execute(text("SELECT DB_NAME()")).scalar())
        # Muestra 5 filas de iButtons por si la tabla existe
        rows = conn.execute(text("SELECT TOP 5 * FROM iButtons")).fetchall()
        print("Top 5 rows count:", len(rows))
        for r in rows:
            try:
                print("ROW mapping keys:", getattr(r, "_mapping", dict(r).keys()))
            except Exception:
                print("ROW repr:", r)
        # Consulta puntual por clave
        clave = 'E00464'
        row = conn.execute(text("SELECT * FROM iButtons WHERE Clave = :c"), {"c": clave}).fetchone()
        print("Row for", clave, "->", row)

if __name__ == "__main__":
    run()