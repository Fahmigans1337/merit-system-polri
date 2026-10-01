#!/bin/bash
set -e

echo "=================================================="
echo " Merit System Personel Polri - Auto Setup"
echo "=================================================="

# ── 1. Cek & Start PostgreSQL ──────────────────────────
echo ""
echo "[1/5] Setup PostgreSQL..."

# Install jika belum ada
if ! command -v psql &> /dev/null; then
    echo "  Installing PostgreSQL..."
    sudo apt-get update -qq
    sudo apt-get install -y postgresql postgresql-contrib -qq
fi

# Start service
sudo service postgresql start 2>/dev/null || sudo pg_ctlcluster 15 main start 2>/dev/null || true

# Tunggu PostgreSQL ready
sleep 2

# ── 2. Buat database & user ───────────────────────────
echo "[2/5] Setup database..."
sudo -u postgres psql -c "CREATE USER merituser WITH PASSWORD 'merit2026';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE merit_polri OWNER merituser;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE merit_polri TO merituser;" 2>/dev/null || true
echo "  Database 'merit_polri' siap!"

# ── 3. Install dependencies ───────────────────────────
echo "[3/5] Install dependencies..."
pip install -q -r requirements.txt

# ── 4. Set environment variables & seed ──────────────
echo "[4/5] Seed database..."
export DATABASE_URL="postgresql+psycopg2://merituser:merit2026@localhost:5432/merit_polri"
export SECRET_KEY="merit-system-polri-secret-2026"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=1440
export REFRESH_TOKEN_EXPIRE_DAYS=7
export DEBUG=True
export PYTHONIOENCODING=utf-8

python -X utf8 seed.py

# ── 5. Jalankan server ────────────────────────────────
echo "[5/5] Starting server..."
echo ""
echo "=================================================="
echo " SERVER RUNNING!"
echo " Swagger UI : http://localhost:8000/docs"
echo " ReDoc      : http://localhost:8000/redoc"
echo "=================================================="
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
