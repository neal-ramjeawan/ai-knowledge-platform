from pathlib import Path

from app.db import get_connection

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def get_migration_paths():
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def split_sql_statements(sql: str) -> list[str]:
    statements = []
    for statement in sql.split(";"):
        cleaned = statement.strip()
        if cleaned:
            statements.append(cleaned)

    return statements


def apply_migrations(conn):
    for migration_path in get_migration_paths():
        sql = migration_path.read_text(encoding="utf-8")

        for statement in split_sql_statements(sql):
            with conn.cursor() as cur:
                cur.execute(statement)


def initialize_database():
    with get_connection() as conn:
        apply_migrations(conn)
