"""Seed manual (opsional). Aplikasi sudah seed otomatis saat start; script ini untuk dijalankan terpisah.

  python -X utf8 seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.bootstrap import wait_for_database  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.seed_data import seed_database  # noqa: E402

wait_for_database(settings.DB_CONNECT_RETRIES, settings.DB_CONNECT_DELAY)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    seed_database(db)
except Exception as exc:
    print(f"\nError saat seeding: {exc}")
    db.rollback()
    raise
finally:
    db.close()
