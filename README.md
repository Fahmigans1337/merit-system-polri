# Merit SDM - Personel Polri

REST API dan Web UI untuk pengelolaan **kualifikasi dan riwayat jabatan personel Polri** (prototype sistem merit).

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL
- **Autentikasi:** JWT (access token 1 hari, refresh token 7 hari)
- **Otorisasi:** RBAC dengan 2 role (Admin SSDM dan Operator Satker)
- **Web UI:** login + dashboard Admin/Operator, dilayani langsung oleh FastAPI (tanpa build tambahan)
- **Dokumentasi API:** Swagger UI dan ReDoc

## Fitur

- CRUD personel: nama, NRP/NIP, pangkat, tempat dan tanggal lahir, satuan kerja
- CRUD riwayat jabatan: jabatan, satuan kerja, fungsi, TMT, nivelering, status, keterangan
- Profil personel: identitas, jabatan aktif saat ini, dan riwayat jabatan kronologis (terlama ke terbaru)
- Pencarian dan filter personel (nama, NRP/NIP, pangkat, satuan kerja) dengan pagination
- 22 pangkat Polri (Pati, Pamen, Pama, Bintara, Tamtama), diurutkan dari tertinggi ke terendah
- 46 satuan kerja: 11 satker Mabes, lalu 34 Polda urut dari Aceh sampai Papua Tengah
- Dashboard statistik yang mengikuti role
- Validasi input dan pesan error yang jelas

## Cara Menjalankan

Database **dibuat dan diisi otomatis** saat aplikasi start: menunggu database siap, membuat tabel, lalu mengisi data awal bila masih kosong. Tidak ada langkah seed atau migrasi manual, dan aman dijalankan berulang kali (data tidak digandakan).

### Opsi 1: Docker (paling mudah, memakai PostgreSQL)

```bash
git clone https://github.com/Fahmigans1337/merit-system-polri.git
cd merit-system-polri
docker compose up --build
```

Tunggu sampai muncul `Application startup complete`, lalu buka **http://localhost:8000/**.

- Percobaan pertama mengunduh image PostgreSQL dan Python sehingga bisa memakan waktu beberapa menit, tergantung koneksi internet.
- Port bentrok? Jalankan dengan `APP_PORT=8080 docker compose up --build` (di PowerShell: `$env:APP_PORT=8080; docker compose up --build`).
- Menghentikan: `docker compose down`. Untuk menghapus data juga: `docker compose down -v`.

### Opsi 2: Tanpa Docker (langsung jalan, memakai SQLite)

Butuh Python 3.11 atau lebih baru. Tidak perlu `.env` dan tidak perlu PostgreSQL.

```bash
git clone https://github.com/Fahmigans1337/merit-system-polri.git
cd merit-system-polri
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

Database `merit_polri.db` dibuat otomatis di folder proyek. Hapus file itu untuk mengulang dari data awal.

### Opsi 3: Linux / WSL dengan PostgreSQL lokal

```bash
python3 -m venv venv && source venv/bin/activate
bash run.sh
```

`run.sh` memasang dan menjalankan PostgreSQL, membuat database dan user, memasang dependency, lalu menjalankan server.

### Memakai PostgreSQL sendiri

Set `DATABASE_URL` (awalan wajib `postgresql+psycopg2://`), lalu jalankan uvicorn seperti biasa:

```bash
export DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/merit_polri
python -m uvicorn app.main:app --port 8000
```

Database kosong harus sudah ada. Tabel dan data awal dibuat otomatis, dan aplikasi menunggu sampai database dapat dihubungi (maksimal sekitar 1 menit).

## Alamat Penting

| URL | Keterangan |
|---|---|
| http://localhost:8000/ | Web UI (login + dashboard) |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/openapi.json | Spesifikasi OpenAPI |
| http://localhost:8000/health | Health check |

## Akun Demo

| Username | Password | Role | Satuan Kerja |
|---|---|---|---|
| `admin.ssdm` | `Admin@12345` | ADMIN_SSDM | SSDM POLRI |
| `operator.metro` | `Operator@123` | OPERATOR_SATKER | POLDA METRO JAYA |
| `operator.jabar` | `Operator@123` | OPERATOR_SATKER | POLDA JAWA BARAT |
| `operator.jatim` | `Operator@123` | OPERATOR_SATKER | POLDA JAWA TIMUR |
| `operator.sulsel` | `Operator@123` | OPERATOR_SATKER | POLDA SULAWESI SELATAN |

> Akun ini hanya untuk demo. Ganti password dan `SECRET_KEY` sebelum dipakai di luar lingkungan uji.

## Web UI

| Halaman | Isi |
|---|---|
| Login | Form NRP/Username dan password, "Ingat Saya", akun demo sekali klik |
| Beranda | Modul sesuai role, pengumuman |
| SIPP Personel | Filter pencarian, kartu statistik, daftar personel, tambah/edit/hapus |
| Detail Personel | Data pribadi, jabatan (CRUD), perjalanan karier |
| MDM Satker | Daftar satuan kerja (Admin dapat mengubah) |
| User Management | Khusus Admin |
| Role Management | Penjelasan hak akses tiap role |

## Hak Akses (RBAC)

| Fitur | Admin SSDM | Operator Satker |
|---|---|---|
| Lihat dan kelola personel | Semua satker | Hanya satker sendiri |
| Kelola riwayat jabatan | Semua satker | Hanya satker sendiri |
| Lihat daftar satker | Ya | Ya |
| Tambah/ubah/hapus satker | Ya | Tidak (403) |
| Manajemen pengguna | Ya | Tidak (403) |
| Statistik dashboard | Seluruh satker | Satker sendiri |

## Endpoint REST API

Base URL: `/api/v1`. Semua endpoint (kecuali login, refresh, dan health) memerlukan header `Authorization: Bearer <access_token>`.

| Method | Endpoint | Keterangan |
|---|---|---|
| POST | `/auth/login` | Login, mengembalikan access dan refresh token |
| POST | `/auth/refresh` | Minta access token baru |
| GET | `/auth/me` | Data pengguna yang sedang login |
| GET | `/dashboard/stats` | Statistik sesuai role |
| GET, POST | `/users` | Daftar dan tambah pengguna (Admin) |
| GET, PUT, DELETE | `/users/{user_id}` | Detail, ubah, hapus pengguna (Admin) |
| GET, POST | `/satker` | Daftar satker, tambah satker (Admin) |
| GET, PUT, DELETE | `/satker/{satker_id}` | Detail satker, ubah dan hapus (Admin) |
| GET, POST | `/personel` | Daftar (filter + pagination) dan tambah personel |
| GET, PUT, DELETE | `/personel/{personel_id}` | Profil lengkap, ubah, hapus personel |
| GET, POST | `/personel/{personel_id}/riwayat-jabatan` | Daftar dan tambah riwayat jabatan |
| GET, PUT, DELETE | `/personel/{personel_id}/riwayat-jabatan/{rj_id}` | Detail, ubah, hapus riwayat jabatan |

Filter `GET /personel`: `skip`, `limit` (maks 100), `nama`, `nrp_nip`, `pangkat`, `satker_id` (khusus Admin).

### Cara memakai di Swagger

1. Buka `POST /api/v1/auth/login`, isi username dan password, lalu Execute.
2. Copy nilai `access_token` (bukan `refresh_token`).
3. Klik **Authorize**, isi `Bearer <access_token>`, lalu Authorize.
4. Field `satker_id` dan `personel_id` selalu berupa **UUID**. Ambil dari `GET /satker` atau `GET /personel`, bukan kode atau nama.

## Aturan Validasi

- Field wajib tidak boleh kosong
- `nrp_nip` unik, hanya huruf, angka, spasi, dan tanda hubung
- `tanggal_lahir` harus sebelum hari ini
- `tanggal_berakhir` tidak boleh sebelum `tanggal_mulai`
- Password minimal 8 karakter
- Username minimal 3 karakter (huruf, angka, titik, strip, underscore)
- Kode satker unik

## Struktur Proyek

```
merit-system-polri/
├── app/
│   ├── main.py            # entrypoint FastAPI, CORS, mount Web UI
│   ├── config.py          # pengaturan dari environment
│   ├── database.py        # koneksi SQLAlchemy
│   ├── core/              # security (JWT, bcrypt), dependencies RBAC, urutan satker/pangkat
│   ├── models/            # tabel database
│   ├── schemas/           # validasi request/response (Pydantic)
│   ├── crud/              # akses data
│   ├── routers/           # endpoint API
│   └── static/            # Web UI (index.html, css, js, img)
├── alembic/               # migrasi database
├── seed.py                # data awal
├── run.sh                 # auto setup + jalankan (Linux/WSL)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── Merit_System_Polri.postman_collection.json
```

## Skema Database

```
satker           id, nama, kode (unik), deskripsi
users            id, username (unik), email (unik), password_hash, role, satker_id, is_active
personel         id, nama, nrp_nip (unik), pangkat, tempat_lahir, tanggal_lahir, satker_id
riwayat_jabatan  id, personel_id (cascade), jabatan, satuan_kerja, fungsi, tanggal_mulai,
                 tanggal_berakhir, nivelering_jabatan, status_jabatan, keterangan
```

Seluruh `id` disimpan sebagai string UUID (`String(36)`) agar kompatibel dengan PostgreSQL dan SQLite.

## Environment Variable

Salin `.env.example` menjadi `.env`, lalu sesuaikan.

| Variabel | Keterangan |
|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@host:5432/merit_polri` atau `sqlite:///./merit_polri.db` |
| `SECRET_KEY` | Kunci penandatangan JWT (wajib diganti) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default 1440 (1 hari) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Default 7 |

URL database PostgreSQL harus memakai awalan `postgresql+psycopg2://`.

## Pemecahan Masalah

| Masalah | Solusi |
|---|---|
| `Error: No such option '--reload\r'` | `run.sh` terubah menjadi CRLF. Jalankan `sed -i 's/\r$//' run.sh` lalu ulangi |
| `Database sudah memiliki data. Skip seeding.` | Normal. Untuk mengisi ulang: `sudo -u postgres psql -c "DROP DATABASE merit_polri;"` lalu `bash run.sh` |
| Data satker lama (hanya 4) masih tampil | Database lama belum direset. Drop database lalu jalankan `bash run.sh` |
| `postgresql: unrecognized service` | Jalankan `sudo service postgresql start` di WSL |
| `Address already in use` (port 8000) | Hentikan proses lama dengan Ctrl+C, atau ubah port pada perintah uvicorn |
| Login `Username atau password salah` | Pastikan tidak ada spasi di akhir username |
| UI tidak berubah setelah update | Tekan Ctrl+F5 untuk memuat ulang cache browser |

## Postman

Impor `Merit_System_Polri.postman_collection.json` ke Postman. Jalankan request Login lebih dulu, token tersimpan otomatis untuk request berikutnya.
