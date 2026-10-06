"""Auto setup database saat aplikasi start.

Urutan: tunggu database siap (retry) -> buat tabel -> isi data awal bila masih kosong.
Aman dijalankan berulang kali (idempotent). Nonaktifkan dengan AUTO_SETUP=false.
"""
import logging
import time

from sqlalchemy import text

from app.config import settings
from app.database import Base, SessionLocal, engine
import app.models  # noqa: F401  (mendaftarkan semua model ke metadata)

log = logging.getLogger("uvicorn.error")


def wait_for_database(retries: int, delay: float) -> None:
    """Coba konek ke database sampai berhasil (berguna saat PostgreSQL di Docker masih booting)."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            if attempt > 1:
                log.info("Database siap setelah %d percobaan.", attempt)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            log.warning("Menunggu database (%d/%d)...", attempt, retries)
            time.sleep(delay)
    raise RuntimeError(
        f"Database tidak dapat dihubungi setelah {retries} percobaan. "
        f"Periksa DATABASE_URL. Error terakhir: {last_error}"
    )


def bootstrap() -> None:
    if not settings.AUTO_SETUP:
        log.info("AUTO_SETUP=false: lewati pembuatan tabel dan seed.")
        return

    wait_for_database(settings.DB_CONNECT_RETRIES, settings.DB_CONNECT_DELAY)
    Base.metadata.create_all(bind=engine)

    from app.seed_data import seed_database  # import di sini agar modul ringan saat tidak dipakai

    db = SessionLocal()
    try:
        seed_database(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
