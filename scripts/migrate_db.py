#!/usr/bin/env python3
"""
Migración de datos: Postgres origen → Supabase destino (o cualquier Postgres).

- Crea el esquema en el destino usando exactamente los modelos ORM de la app
  (garantiza que coincida con lo que FastAPI espera; NO usa el SQL de
  database/migrations que está desactualizado).
- Copia users → documents → verifications (orden de claves foráneas).
- Idempotente: se puede re-ejecutar; usa ON CONFLICT DO NOTHING.
- Verifica conteos y una muestra al final. Exit code 0 = OK, 1 = fallo.

Uso:
    venv/bin/python scripts/migrate_db.py \
        --source 'postgresql://...' --dest 'postgresql://...'

    # Solo revisar, no escribe nada:
    venv/bin/python scripts/migrate_db.py --source ... --dest ... --dry-run
"""
import argparse
import os
import sys

# El ORM de la app vive en backend/ (importa src.config...)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))
os.environ.setdefault("DEBUG", "False")  # silencia echo de SQLAlchemy

import psycopg2
from sqlalchemy import create_engine

from src.config.database import Base  # noqa: E402
from src.models import models  # noqa: E402  (registra las tablas en Base)

# Orden de claves foráneas: users <- documents <- verifications
TABLES = ["users", "documents", "verifications"]
BATCH = 500


def normalize_url(url: str) -> str:
    """postgres:// -> postgresql:// y sslmode=require para hosts de Supabase."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if "supabase.co" in url and "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


def connect(url: str, label: str):
    try:
        conn = psycopg2.connect(url, connect_timeout=15)
        conn.autocommit = False
        return conn
    except Exception as exc:  # noqa: BLE001
        print(f"❌ No se pudo conectar a {label}: {exc}")
        sys.exit(1)


def table_columns(conn, table: str) -> list:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return [r[0] for r in cur.fetchall()]


def row_count(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f'SELECT count(*) FROM "{table}"')
        return cur.fetchone()[0]


def create_schema(dest_url: str) -> None:
    """Crea las tablas en el destino tal como las define el ORM."""
    engine = create_engine(dest_url)
    Base.metadata.create_all(bind=engine)
    engine.dispose()


def copy_table(src, dst, table: str):
    src_cols = table_columns(src, table)
    if not src_cols:
        print(f"⚠️  '{table}' no existe en el origen — se omite.")
        return None

    dst_cols = set(table_columns(dst, table))
    cols = [c for c in src_cols if c in dst_cols]
    skipped = [c for c in src_cols if c not in dst_cols]
    if skipped:
        print(f"   columnas del origen que el destino no tiene (se omiten): {skipped}")

    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(f'"{c}"' for c in cols)
    insert_sql = (
        f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders}) '
        "ON CONFLICT DO NOTHING"
    )

    with src.cursor() as cur:
        cur.execute(f'SELECT {col_list} FROM "{table}"')
        rows = cur.fetchall()

    with dst.cursor() as cur:
        for i in range(0, len(rows), BATCH):
            cur.executemany(insert_sql, rows[i : i + BATCH])
    dst.commit()
    return len(rows), skipped


def main() -> int:
    ap = argparse.ArgumentParser(description="Migra users/documents/verifications")
    ap.add_argument("--source", required=True, help="URL del Postgres origen (Render)")
    ap.add_argument("--dest", required=True, help="URL del Postgres destino (Supabase)")
    ap.add_argument("--dry-run", action="store_true", help="No escribe nada")
    args = ap.parse_args()

    src_url = normalize_url(args.source)
    dst_url = normalize_url(args.dest)

    src = connect(src_url, "origen")
    dst = connect(dst_url, "destino")

    print("== Conteos en el ORIGEN ==")
    source_counts = {}
    for t in TABLES:
        try:
            source_counts[t] = row_count(src, t)
            print(f"   {t}: {source_counts[t]}")
        except Exception:  # noqa: BLE001
            source_counts[t] = None
            print(f"   {t}: (no existe)")

    if args.dry_run:
        print("\n🔎 DRY RUN: no se escribió nada. (El esquema del destino se "
              "crea solo cuando NO se usa --dry-run)")
        return 0

    print("\n== Creando esquema en el destino (desde el ORM) ==")
    create_schema(dst_url)
    for t in TABLES:
        print(f"   {t}: {'OK' if table_columns(dst, t) else 'FALLO'}")

    print("\n== Copiando datos ==")
    failures = []
    for t in TABLES:
        if source_counts.get(t) is None:
            continue
        try:
            result = copy_table(src, dst, t)
            if result is None:
                continue
            total, _skipped = result
            print(f"   {t}: {total} filas leídas e insertadas")
        except Exception as exc:  # noqa: BLE001
            dst.rollback()
            failures.append(t)
            print(f"   {t}: ❌ ERROR — {exc}")

    print("\n== Verificación final ==")
    ok = not failures
    for t in TABLES:
        s = source_counts.get(t)
        if s is None:
            continue
        d = row_count(dst, t)
        status = "✅" if s == d else "❌"
        print(f"   {t}: origen={s} destino={d} {status}")
        if s != d:
            ok = False

    # Muestra: el documento más reciente debe existir en el destino
    try:
        with src.cursor() as cur:
            cur.execute('SELECT id FROM documents ORDER BY created_at DESC LIMIT 1')
            row = cur.fetchone()
        if row:
            with dst.cursor() as cur:
                cur.execute('SELECT count(*) FROM documents WHERE id = %s', (row[0],))
                found = cur.fetchone()[0]
            print(f"   muestra (último documento): {'✅' if found else '❌'}")
            ok = ok and bool(found)
    except Exception as exc:  # noqa: BLE001
        print(f"   muestra: ⚠️  no se pudo verificar ({exc})")

    print("\n" + ("✅ MIGRACIÓN VERIFICADA — listo para cambiar DATABASE_URL en Render"
                  if ok else
                  "❌ VERIFICACIÓN FALLIDA — NO cambies DATABASE_URL todavía"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
