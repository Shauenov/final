# seeds/seed_users.py
import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
import bcrypt

# DATABASE_URL должен быть вида: postgresql+psycopg://user:pass@host:5432/dbname
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set")

# Пароли можно переопределить через ENV
ADMIN_PASS = os.environ.get("ADMIN_PASS", "Admin#12345")
USER_PASS  = os.environ.get("USER_PASS",  "User#12345")

ADMIN = {
    "id": str(uuid.uuid4()),
    "full_name": "Admin User",
    "phone": "+77010000001",
    "password": ADMIN_PASS,
    "role": "admin",
}

USER = {
    "id": str(uuid.uuid4()),
    "full_name": "Regular User",
    "phone": "+77010000002",
    "password": USER_PASS,
    "role": "user",
}

def hash_pw(p: str) -> str:
    return bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def upsert_user(conn, u):
    now = datetime.now(timezone.utc)
    params = {
        "id": u["id"],
        "full_name": u["full_name"],
        "phone": u["phone"],
        "password_hash": hash_pw(u["password"]),
        "role": u["role"],
        "created_at": now,
    }

    # Если у тебя в users уникальный индекс по phone (рекомендуется),
    # это upsert сработает. Если нет — см. комментарий ниже.
    sql = text("""
    INSERT INTO users (id, full_name, phone, password_hash, role, is_active, created_at)
    VALUES (:id, :full_name, :phone, :password_hash, :role, TRUE, :created_at)
    ON CONFLICT (phone) DO UPDATE
    SET full_name = EXCLUDED.full_name,
        password_hash = EXCLUDED.password_hash,
        role = EXCLUDED.role,
        is_active = TRUE
    """)
    conn.execute(sql, params)

def ensure_table_exists(conn):
    q = text("""
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    """)
    if conn.execute(q).scalar() != 1:
        raise RuntimeError("Table 'users' not found. Run migrations first.")

def main():
    engine = create_engine(DATABASE_URL, future=True)
    with engine.begin() as conn:
        ensure_table_exists(conn)
        upsert_user(conn, ADMIN)
        upsert_user(conn, USER)
    print("Seeded: admin + user")
    print(f"Admin phone: {ADMIN['phone']}  password: {ADMIN_PASS}")
    print(f"User  phone: {USER['phone']}   password: {USER_PASS}")

if __name__ == "__main__":
    main()
