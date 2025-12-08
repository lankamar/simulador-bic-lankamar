"""
Módulo de conexión a base de datos SQLite
Simulador BIC Lankamar - Sistema de Autenticación
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Ruta de la base de datos (junto a este archivo)
DB_PATH = Path(__file__).resolve().parent / "auth.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


@contextmanager
def get_conn():
    """
    Context manager para conexiones a SQLite.
    Uso:
        with get_conn() as conn:
            conn.execute("SELECT * FROM users")
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    conn.execute("PRAGMA foreign_keys = ON")  # Habilitar FK
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db(force: bool = False):
    """
    Inicializa la base de datos ejecutando schema.sql
    
    Args:
        force: Si True, elimina la DB existente y la recrea
    """
    if force and DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[!] Base de datos eliminada: {DB_PATH}")
    
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el schema: {SCHEMA_PATH}")
    
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    
    with get_conn() as conn:
        conn.executescript(schema)
    
    print(f"[OK] Base de datos inicializada en: {DB_PATH}")


def get_db_stats() -> dict:
    """Retorna estadísticas de la base de datos"""
    with get_conn() as conn:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        invites_count = conn.execute("SELECT COUNT(*) FROM invites").fetchone()[0]
        invites_pending = conn.execute(
            "SELECT COUNT(*) FROM invites WHERE used_at IS NULL"
        ).fetchone()[0]
    
    return {
        "users": users_count,
        "invites_total": invites_count,
        "invites_pending": invites_pending,
        "db_path": str(DB_PATH),
        "db_exists": DB_PATH.exists(),
        "db_size_kb": round(DB_PATH.stat().st_size / 1024, 2) if DB_PATH.exists() else 0
    }


if __name__ == "__main__":
    print("[*] Inicializando base de datos SQLite...")
    init_db()
    print("\n[i] Estadisticas:")
    stats = get_db_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
