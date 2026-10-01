# Merit System Personel Polri
## REST API Prototype — Take Home Test

![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat-square&logo=jsonwebtokens)

Prototype aplikasi **Merit System Personel Polri** berbasis REST API untuk pengelolaan data kualifikasi dan riwayat jabatan personel Polri secara terintegrasi.

---

## 📋 Fitur Utama

| Fitur | Keterangan |
|---|---|
| **CRUD Personel** | Tambah, lihat, ubah, hapus data personel |
| **CRUD Riwayat Jabatan** | Kelola histori jabatan per personel (kronologis) |
| **RBAC** | Role-Based Access Control: Admin SSDM & Operator Satker |
| **JWT Auth** | Access token (24 jam) + Refresh token (7 hari) |
| **Validasi Input** | Pydantic v2: format tanggal, field wajib, NRP/NIP unik, dll |
| **Swagger UI** | Dokumentasi API interaktif built-in di `/docs` |
| **Pagination** | Semua list endpoint mendukung `skip` & `limit` |
| **Search & Filter** | Filter personel berdasarkan nama, NRP/NIP, pangkat, satker |
| **Docker** | Deploy dengan satu perintah `docker compose up` |

---

## 🏗️ Arsitektur & Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                   REST API (FastAPI)                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  /auth   │  │  /users  │  │ /satker  │  │/personel │  │
│  │  /auth   │  │  /users  │  │ /satker  │  │/personel │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│         ↓              ↓            ↓              ↓        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             CRUD Layer (SQLAlchemy ORM)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↓                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              PostgreSQL 15 Database                 │   │
│  │  users │ satker │ personel │ riwayat_jabatan        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Teknologi |
|---|---|
| Framework | FastAPI 0.109 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Auth | JWT (python-jose + passlib bcrypt) |
| Validasi | Pydantic v2 |
| Dokumentasi | Swagger UI / OpenAPI 3.0 (built-in) |
| Migrasi | Alembic |
| Deployment | Docker + Docker Compose |

---

## 🗂️ Struktur Proyek

```
merit-system-polri/
├── app/
│   ├── main.py                   # Entry point FastAPI
│   ├── config.py                 # Konfigurasi & settings (env)
│   ├── database.py               # SQLAlchemy engine & session
│   ├── models/                   # ORM Models
│   │   ├── user.py               # Model User + enum UserRole
│   │   ├── satker.py             # Model Satuan Kerja
│   │   ├── personel.py           # Model Personel
│   │   └── riwayat_jabatan.py    # Model Riwayat Jabatan + enum Status
│   ├── schemas/                  # Pydantic Schemas (request/response)
│   │   ├── auth.py               # Token, LoginRequest
│   │   ├── user.py               # UserCreate, UserUpdate, UserResponse
│   │   ├── satker.py             # SatkerCreate, SatkerUpdate, SatkerResponse
│   │   ├── personel.py           # PersonelCreate, PersonelUpdate, PersonelResponse
│   │   └── riwayat_jabatan.py    # RiwayatJabatanCreate, Update, Response
│   ├── crud/                     # Database CRUD operations
│   │   ├── user.py
│   │   ├── satker.py
│   │   ├── personel.py
│   │   └── riwayat_jabatan.py
│   ├── routers/                  # API Route Handlers
│   │   ├── auth.py               # POST /login, /refresh, GET /me
│   │   ├── users.py              # CRUD /users (Admin only)
│   │   ├── satker.py             # CRUD /satker
│   │   ├── personel.py           # CRUD /personel
│   │   └── riwayat_jabatan.py    # CRUD /personel/{id}/riwayat-jabatan
│   └── core/
│       ├── security.py           # JWT & password hashing
│       └── dependencies.py       # FastAPI auth dependencies
├── alembic/                      # Database migrations
├── seed.py                       # Script data awal (dummy data)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## 🚀 Cara Menjalankan

### Metode 1: Docker Compose (Recommended)

**Prasyarat:** Docker & Docker Compose terinstall.

```bash
# 1. Clone repository
git clone <repository-url>
cd merit-system-polri

# 2. Jalankan semua service
docker compose up --build

# API akan tersedia di: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

> Seeder otomatis berjalan dan mengisi data awal saat pertama kali dijalankan.

---

### Metode 2: Lokal (Manual)

**Prasyarat:** Python 3.11+, PostgreSQL 15

```bash
# 1. Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Salin dan sesuaikan .env
cp .env.example .env
# Edit DATABASE_URL di file .env

# 4. Isi data awal
python seed.py

# 5. Jalankan server
uvicorn app.main:app --reload --port 8000
```

---

## 🔑 Autentikasi

API menggunakan **JWT Bearer Token**. Langkah autentikasi:

### 1. Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin.ssdm",
  "password": "Admin@12345"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

### 2. Gunakan Token

Sertakan header di setiap request:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR...
```

---

## 👥 Role & Kewenangan

| Role | Kewenangan |
|---|---|
| `ADMIN_SSDM` | Full CRUD: semua personel, semua satker, manajemen user |
| `OPERATOR_SATKER` | CRUD personel & riwayat jabatan **hanya di satkernya sendiri** |

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Login, dapatkan token | ❌ |
| POST | `/api/v1/auth/refresh` | Refresh access token | ❌ |
| GET | `/api/v1/auth/me` | Info user aktif | ✅ |

### User Management *(Admin Only)*

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/users` | List semua user |
| POST | `/api/v1/users` | Buat user baru |
| GET | `/api/v1/users/{id}` | Detail user |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Hapus user |

### Satuan Kerja

| Method | Endpoint | Deskripsi | Role |
|---|---|---|---|
| GET | `/api/v1/satker` | List semua satker | All |
| POST | `/api/v1/satker` | Tambah satker | Admin |
| GET | `/api/v1/satker/{id}` | Detail satker | All |
| PUT | `/api/v1/satker/{id}` | Update satker | Admin |
| DELETE | `/api/v1/satker/{id}` | Hapus satker | Admin |

### Personel

| Method | Endpoint | Deskripsi | Filter |
|---|---|---|---|
| GET | `/api/v1/personel` | List personel (paginated) | `nama`, `nrp_nip`, `pangkat`, `satker_id` |
| POST | `/api/v1/personel` | Tambah personel | — |
| GET | `/api/v1/personel/{id}` | Profil lengkap + riwayat | — |
| PUT | `/api/v1/personel/{id}` | Update personel | — |
| DELETE | `/api/v1/personel/{id}` | Hapus personel (cascade) | — |

### Riwayat Jabatan

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/v1/personel/{id}/riwayat-jabatan` | List riwayat (kronologis) |
| POST | `/api/v1/personel/{id}/riwayat-jabatan` | Tambah riwayat jabatan |
| GET | `/api/v1/personel/{id}/riwayat-jabatan/{rj_id}` | Detail riwayat jabatan |
| PUT | `/api/v1/personel/{id}/riwayat-jabatan/{rj_id}` | Update riwayat jabatan |
| DELETE | `/api/v1/personel/{id}/riwayat-jabatan/{rj_id}` | Hapus riwayat jabatan |

---

## ✅ Validasi Input

| Field | Aturan Validasi |
|---|---|
| `tanggal_lahir` | Format DATE (YYYY-MM-DD), harus lebih awal dari hari ini |
| `tanggal_mulai` | Format DATE, wajib diisi |
| `tanggal_berakhir` | Opsional, jika diisi harus ≥ `tanggal_mulai` |
| `nrp_nip` | Unik, alfanumerik, wajib diisi |
| `email` | Format email valid, unik per sistem |
| `password` | Minimal 8 karakter |
| `username` | Minimal 3 karakter, alfanumerik + `-`, `_`, `.` |
| Field wajib | Return `422 Unprocessable Entity` jika kosong |

---

## 📚 Akun Demo (Seed Data)

| Username | Password | Role | Satker |
|---|---|---|---|
| `admin.ssdm` | `Admin@12345` | ADMIN_SSDM | SSDM POLRI |
| `operator.metro` | `Operator@123` | OPERATOR_SATKER | Polda Metro Jaya |
| `operator.jabar` | `Operator@123` | OPERATOR_SATKER | Polda Jawa Barat |
| `operator.jatim` | `Operator@123` | OPERATOR_SATKER | Polda Jawa Timur |

---

## 📖 Dokumentasi API

| URL | Deskripsi |
|---|---|
| `http://localhost:8000/docs` | Swagger UI (interaktif) |
| `http://localhost:8000/redoc` | ReDoc (read-only) |
| `http://localhost:8000/openapi.json` | OpenAPI 3.0 JSON Spec |

---

## 🗄️ Skema Database

```
users
  id (UUID PK) | username | email | password_hash | role | satker_id (FK) | is_active

satker
  id (UUID PK) | nama | kode (UNIQUE) | deskripsi

personel
  id (UUID PK) | nama | nrp_nip (UNIQUE) | pangkat | tempat_lahir | tanggal_lahir | satker_id (FK)

riwayat_jabatan
  id (UUID PK) | personel_id (FK) | jabatan | satuan_kerja | fungsi |
  tanggal_mulai | tanggal_berakhir | nivelering_jabatan | status_jabatan | keterangan
```

---

## 🔒 Keamanan

- Password di-hash dengan **bcrypt** (cost factor 12)
- JWT ditandatangani dengan **HS256**
- Setiap endpoint diproteksi dengan autentikasi JWT
- RBAC memastikan isolasi data per satker
- Secret key wajib diganti via environment variable di production

---

## 📞 Kontribusi & Lisensi

Proyek ini dibuat untuk keperluan **Seleksi Kemampuan Pemrograman** SSDM Polri.

> Waktu Pelaksanaan: 1–7 Oktober 2026 | Durasi: 7 Hari | Metode: Take Home Test
