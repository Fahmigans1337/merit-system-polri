<<<<<<< HEAD
﻿# Merit System Personel Polri
=======
# Merit System Personel Polri
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8
## REST API Prototype — Take Home Test Seleksi Kemampuan Pemrograman

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11--3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat-square&logo=jsonwebtokens)
![License](https://img.shields.io/badge/Internal_Use-Polri_SSDM-blue?style=flat-square)

> **Seleksi Kemampuan Pemrograman** — CRUD Sistem Merit Personel Polri: Kualifikasi dan Riwayat Jabatan
> Waktu Pelaksanaan: 1–7 Oktober 2026 | Durasi: 7 Hari | Metode: Take Home Test

---

<<<<<<< HEAD
## 📋 Deskripsi
=======
## Deskripsi
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

Prototype aplikasi **Merit System Personel Polri** berbasis REST API untuk pengelolaan data kualifikasi dan riwayat jabatan personel Polri secara terintegrasi.

Fitur utama:
- **CRUD Personel** — kelola data kualifikasi personel lengkap
- **CRUD Riwayat Jabatan** — histori jabatan kronologis per personel
- **Validasi Input** — Pydantic v2 dengan aturan ketat (format tanggal, NRP unik, dll)
- **JWT Authentication** — access token (24 jam) + refresh token (7 hari)
- **RBAC** — Role-Based Access Control (Admin SSDM vs Operator Satker)
- **Swagger UI** — dokumentasi API interaktif otomatis di `/docs`
- **PostgreSQL** — database produksi yang handal

---

<<<<<<< HEAD
## 🏗️ Tech Stack
=======
## Tech Stack
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

| Komponen | Teknologi |
|---|---|
| Framework | FastAPI (Python) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x |
| Validasi | Pydantic v2 |
| Auth | JWT (python-jose + bcrypt) |
| Dokumentasi | Swagger UI / OpenAPI 3.0 |
| Migrasi | Alembic |
| Deployment | Docker + Docker Compose |

---

## Struktur Proyek

```
merit-system-polri/
├── app/
│   ├── main.py                    # Entry point FastAPI
│   ├── config.py                  # Konfigurasi environment
│   ├── database.py                # SQLAlchemy engine & session
│   ├── models/                    # ORM Models (SQLAlchemy)
│   │   ├── user.py                # Model User + enum UserRole
│   │   ├── satker.py              # Model Satuan Kerja
│   │   ├── personel.py            # Model Personel
│   │   └── riwayat_jabatan.py     # Model Riwayat Jabatan + enum Status
│   ├── schemas/                   # Pydantic Schemas (validasi request/response)
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── satker.py
│   │   ├── personel.py
│   │   └── riwayat_jabatan.py
│   ├── crud/                      # Logika database CRUD
│   │   ├── user.py
│   │   ├── satker.py
│   │   ├── personel.py
│   │   └── riwayat_jabatan.py
│   ├── routers/                   # API Route Handlers
│   │   ├── auth.py                # Login, refresh, me
│   │   ├── users.py               # Manajemen user (Admin only)
│   │   ├── satker.py              # CRUD Satuan Kerja
│   │   ├── personel.py            # CRUD Personel + profil lengkap
│   │   └── riwayat_jabatan.py     # CRUD Riwayat Jabatan
│   └── core/
│       ├── security.py            # JWT & bcrypt password hashing
│       └── dependencies.py        # FastAPI auth dependencies
├── alembic/                       # Database migrations
│   ├── env.py
│   └── versions/
├── seed.py                        # Script data awal (dummy data)
├── run.sh                         # Auto-setup script (PostgreSQL + seed + server)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── Merit_System_Polri.postman_collection.json
└── README.md
```

---

## Cara Menjalankan

### Metode 1: Script Otomatis `run.sh` (Linux/WSL) — Recommended

Satu perintah untuk install PostgreSQL, buat database, seed data, dan jalankan server:

```bash
git clone https://github.com/Fahmigans1337/merit-system-polri.git
cd merit-system-polri
chmod +x run.sh
bash run.sh
```

Script ini otomatis:
1. Install PostgreSQL jika belum ada
2. Start PostgreSQL service
3. Buat database `merit_polri` dan user
4. Install Python dependencies
5. Seed data awal (tanpa perlu konfigurasi manual)
6. Jalankan server di port 8000

### Metode 2: Docker Compose

```bash
git clone https://github.com/Fahmigans1337/merit-system-polri.git
cd merit-system-polri
docker compose up --build
```

### Metode 3: Manual (tanpa Docker)

```bash
# Clone repo
git clone https://github.com/Fahmigans1337/merit-system-polri.git
cd merit-system-polri

# Install dependencies
pip install -r requirements.txt

# Konfigurasi environment
cp .env.example .env
# Edit .env sesuaikan DATABASE_URL

# Isi data awal
python seed.py

# Jalankan server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Metode 4: SQLite (local dev, tanpa PostgreSQL)

```bash
export DATABASE_URL="sqlite:///./merit_polri.db"
export SECRET_KEY="merit-system-polri-secret-2026"
export ALGORITHM="HS256"
python seed.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 Akses Aplikasi

Setelah server berjalan:

| URL | Keterangan |
|---|---|
| http://localhost:8000/ atau http://localhost:8000/app/ | **Web UI** (login + dashboard Admin/Operator) |
| http://localhost:8000/docs | **Swagger UI** (dokumentasi interaktif) |
| http://localhost:8000/redoc | ReDoc (dokumentasi read-only) |
| http://localhost:8000/openapi.json | OpenAPI 3.0 JSON Spec |
| http://localhost:8000/health | Health check endpoint |

---

<<<<<<< HEAD
## 🔑 Cara Autentikasi di Swagger UI
=======
## Cara Autentikasi di Swagger UI
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

1. Buka **http://localhost:8000/docs**
2. Klik **`POST /api/v1/auth/login`** → **Try it out** → isi username & password → **Execute**
3. Copy nilai `access_token` dari response
<<<<<<< HEAD
4. Klik tombol **🔒 Authorize** (pojok kanan atas)
=======
4. Klik tombol **Authorize** (pojok kanan atas)
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8
5. Masukkan: `Bearer <access_token>`
6. Klik **Authorize** → **Close**
7. Semua endpoint kini bisa diakses dengan hak sesuai role

---

## 👥 Akun Demo (setelah seed.py dijalankan)

| Username | Password | Role | Satker |
|---|---|---|---|
| `admin.ssdm` | `Admin@12345` | ADMIN_SSDM | SSDM Polri |
| `operator.metro` | `Operator@123` | OPERATOR_SATKER | Polda Metro Jaya |
| `operator.jabar` | `Operator@123` | OPERATOR_SATKER | Polda Jawa Barat |
| `operator.jatim` | `Operator@123` | OPERATOR_SATKER | Polda Jawa Timur |

---

<<<<<<< HEAD
## 🔐 Role & Kewenangan (RBAC)
=======
## Role & Kewenangan (RBAC)
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

| Fitur | ADMIN_SSDM | OPERATOR_SATKER |
|---|---|---|
| Lihat semua personel (semua satker) | ✅ | ❌ |
| Lihat personel satker sendiri | ✅ | ✅ |
| Tambah/edit/hapus personel satker sendiri | ✅ | ✅ |
| Kelola riwayat jabatan satker sendiri | ✅ | ✅ |
| Manajemen user (CRUD) | ✅ | ❌ |
| CRUD Satuan Kerja | ✅ | ❌ (read only) |
| Filter personel per satker | ✅ | ❌ (otomatis) |
<<<<<<< HEAD

---

## 📡 Daftar API Endpoints

Base URL: `http://localhost:8000/api/v1`

### 🔐 Authentication

| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| POST | `/auth/login` | Login, dapat access & refresh token | ❌ |
| POST | `/auth/refresh` | Perbarui access token dengan refresh token | ❌ |
| GET | `/auth/me` | Info profil user yang sedang login | ✅ |

### 👥 User Management *(Admin SSDM Only)*

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/users` | List semua pengguna sistem |
| POST | `/users` | Buat akun pengguna baru |
| GET | `/users/{id}` | Detail pengguna |
| PUT | `/users/{id}` | Update data pengguna |
| DELETE | `/users/{id}` | Hapus pengguna |

### 🏢 Satuan Kerja

| Method | Endpoint | Deskripsi | Role |
|---|---|---|---|
| GET | `/satker` | List semua satker | Semua |
| POST | `/satker` | Tambah satker baru | Admin |
| GET | `/satker/{id}` | Detail satker | Semua |
| PUT | `/satker/{id}` | Update satker | Admin |
| DELETE | `/satker/{id}` | Hapus satker | Admin |

### 👮 Personel

| Method | Endpoint | Deskripsi | Query Params |
|---|---|---|---|
| GET | `/personel` | List personel dengan filter & pagination | `nama`, `nrp_nip`, `pangkat`, `satker_id`, `skip`, `limit` |
| POST | `/personel` | Tambah personel baru | — |
| GET | `/personel/{id}` | Profil lengkap + riwayat jabatan kronologis | — |
| PUT | `/personel/{id}` | Update data personel | — |
| DELETE | `/personel/{id}` | Hapus personel + seluruh riwayat (cascade) | — |

### 📋 Riwayat Jabatan

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/personel/{id}/riwayat-jabatan` | List riwayat jabatan (terlama → terbaru) |
| POST | `/personel/{id}/riwayat-jabatan` | Tambah riwayat jabatan baru |
| GET | `/personel/{id}/riwayat-jabatan/{rj_id}` | Detail satu riwayat jabatan |
| PUT | `/personel/{id}/riwayat-jabatan/{rj_id}` | Update riwayat jabatan |
| DELETE | `/personel/{id}/riwayat-jabatan/{rj_id}` | Hapus riwayat jabatan |

---

## ✅ Validasi Input

| Field | Aturan |
|---|---|
| `tanggal_lahir` | Format DATE (YYYY-MM-DD), harus sebelum hari ini |
| `tanggal_mulai` | Format DATE, wajib diisi |
| `tanggal_berakhir` | Opsional; jika diisi harus ≥ `tanggal_mulai` |
| `nrp_nip` | Wajib unik di seluruh sistem |
| `email` | Format email valid, unik per sistem |
| `password` | Minimal 8 karakter |
| `username` | Minimal 3 karakter, alfanumerik + `.`, `-`, `_` |
| `nama` | Tidak boleh kosong atau hanya spasi |
| Field wajib kosong | Response `422 Unprocessable Entity` |
| Data duplikat | Response `400 Bad Request` |
| Akses tidak berwenang | Response `403 Forbidden` |
| Data tidak ditemukan | Response `404 Not Found` |
=======
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

---

## Daftar API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Authentication

| Method | Endpoint | Deskripsi | Auth |
|---|---|---|---|
| POST | `/auth/login` | Login, dapat access & refresh token | ❌ |
| POST | `/auth/refresh` | Perbarui access token dengan refresh token | ❌ |
| GET | `/auth/me` | Info profil user yang sedang login | ✅ |

### User Management *(Admin SSDM Only)*

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/users` | List semua pengguna sistem |
| POST | `/users` | Buat akun pengguna baru |
| GET | `/users/{id}` | Detail pengguna |
| PUT | `/users/{id}` | Update data pengguna |
| DELETE | `/users/{id}` | Hapus pengguna |

### Satuan Kerja

| Method | Endpoint | Deskripsi | Role |
|---|---|---|---|
| GET | `/satker` | List semua satker | Semua |
| POST | `/satker` | Tambah satker baru | Admin |
| GET | `/satker/{id}` | Detail satker | Semua |
| PUT | `/satker/{id}` | Update satker | Admin |
| DELETE | `/satker/{id}` | Hapus satker | Admin |

### Personel

| Method | Endpoint | Deskripsi | Query Params |
|---|---|---|---|
| GET | `/personel` | List personel dengan filter & pagination | `nama`, `nrp_nip`, `pangkat`, `satker_id`, `skip`, `limit` |
| POST | `/personel` | Tambah personel baru | — |
| GET | `/personel/{id}` | Profil lengkap + riwayat jabatan kronologis | — |
| PUT | `/personel/{id}` | Update data personel | — |
| DELETE | `/personel/{id}` | Hapus personel + seluruh riwayat (cascade) | — |

### Riwayat Jabatan

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/personel/{id}/riwayat-jabatan` | List riwayat jabatan (terlama → terbaru) |
| POST | `/personel/{id}/riwayat-jabatan` | Tambah riwayat jabatan baru |
| GET | `/personel/{id}/riwayat-jabatan/{rj_id}` | Detail satu riwayat jabatan |
| PUT | `/personel/{id}/riwayat-jabatan/{rj_id}` | Update riwayat jabatan |
| DELETE | `/personel/{id}/riwayat-jabatan/{rj_id}` | Hapus riwayat jabatan |

---

## Validasi Input

| Field | Aturan |
|---|---|
| `tanggal_lahir` | Format DATE (YYYY-MM-DD), harus sebelum hari ini |
| `tanggal_mulai` | Format DATE, wajib diisi |
| `tanggal_berakhir` | Opsional; jika diisi harus ≥ `tanggal_mulai` |
| `nrp_nip` | Wajib unik di seluruh sistem |
| `email` | Format email valid, unik per sistem |
| `password` | Minimal 8 karakter |
| `username` | Minimal 3 karakter, alfanumerik + `.`, `-`, `_` |
| `nama` | Tidak boleh kosong atau hanya spasi |
| Field wajib kosong | Response `422 Unprocessable Entity` |
| Data duplikat | Response `400 Bad Request` |
| Akses tidak berwenang | Response `403 Forbidden` |
| Data tidak ditemukan | Response `404 Not Found` |

---

## Skema Database

```
satker
  id (UUID) | nama | kode (UNIQUE) | deskripsi | created_at | updated_at

users
  id (UUID) | username (UNIQUE) | email (UNIQUE) | password_hash |
  role (ADMIN_SSDM/OPERATOR_SATKER) | satker_id (FK) | is_active

personel
  id (UUID) | nama | nrp_nip (UNIQUE) | pangkat | tempat_lahir |
  tanggal_lahir | satker_id (FK) | created_at | updated_at

riwayat_jabatan
  id (UUID) | personel_id (FK, CASCADE) | jabatan | satuan_kerja | fungsi |
  tanggal_mulai | tanggal_berakhir | nivelering_jabatan |
  status_jabatan (AKTIF/NON_AKTIF) | keterangan | created_at | updated_at
```

---

<<<<<<< HEAD
## 📮 Postman Collection
=======
## Postman Collection
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

File `Merit_System_Polri.postman_collection.json` tersedia di root repository.

**Cara import:**
1. Buka Postman
2. **Import** → pilih file `Merit_System_Polri.postman_collection.json`
3. Jalankan request `[AUTH] Login Admin SSDM` → token otomatis tersimpan
4. Semua endpoint siap ditest

---

<<<<<<< HEAD
## 🔒 Keamanan
=======
## Keamanan
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

- Password di-hash dengan **bcrypt** (cost factor 12)
- JWT ditandatangani dengan **HS256**
- Setiap endpoint diproteksi autentikasi JWT
- RBAC memastikan isolasi data antar satker
- `SECRET_KEY` wajib diganti di environment production

---

<<<<<<< HEAD
## 📞 Informasi
=======
## Informasi
>>>>>>> 126ed430cebf8fa206b0b3ecabef37d10ab978e8

> Proyek ini dibuat untuk keperluan **Seleksi Kemampuan Pemrograman** SSDM Polri.
> Waktu Pelaksanaan: 1–7 Oktober 2026 | Durasi: 7 Hari | Metode: Take Home Test
> By: Bripda Zul Fahmi Rizki 
