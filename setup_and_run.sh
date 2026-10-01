#!/bin/bash
set -e

echo "======================================"
echo " MERIT SYSTEM POLRI - AUTO SETUP"
echo "======================================"

cd ~/merit-system-polri

# 1. Install PostgreSQL jika belum ada
echo ""
echo "[1/5] Install PostgreSQL..."
if ! command -v psql &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y postgresql postgresql-contrib
    echo "     PostgreSQL installed!"
else
    echo "     PostgreSQL sudah ada: $(psql --version)"
fi

# 2. Start PostgreSQL service
echo ""
echo "[2/5] Start PostgreSQL service..."
sudo service postgresql start
sleep 2
echo "     PostgreSQL running!"

# 3. Buat database dan user
echo ""
echo "[3/5] Buat database merit_polri..."
sudo -u postgres psql -c "CREATE USER merit_user WITH PASSWORD 'merit_pass_2026';" 2>/dev/null || echo "     User sudah ada, skip."
sudo -u postgres psql -c "CREATE DATABASE merit_polri OWNER merit_user;" 2>/dev/null || echo "     Database sudah ada, skip."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE merit_polri TO merit_user;" 2>/dev/null
echo "     Database siap!"

# 4. Tulis .env langsung (no cat heredoc)
echo ""
echo "[4/5] Setup .env PostgreSQL..."
python3 -c "
content = '''DATABASE_URL=postgresql+psycopg2://merit_user:merit_pass_2026@localhost:5432/merit_polri
SECRET_KEY=merit-system-polri-secret-key-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=True
'''
with open('.env', 'w') as f:
    f.write(content)
print('     .env berhasil dibuat!')
"

# 5. Install dependencies
echo ""
echo "[5/6] Install Python dependencies..."
pip install -r requirements.txt -q
echo "     Dependencies OK!"

# 6. Seed database
echo ""
echo "[6/6] Seed database..."
python3 -X utf8 seed.py

# 7. Jalankan server
echo ""
echo "======================================"
echo " SERVER STARTING..."
echo "======================================"
echo ""
echo "  Swagger UI : http://localhost:8000/docs"
echo "  ReDoc      : http://localhost:8000/redoc"
echo ""
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
