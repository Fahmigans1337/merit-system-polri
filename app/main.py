import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.core.bootstrap import bootstrap
from app.routers import auth, users, satker, personel, riwayat_jabatan, dashboard


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Auto setup: tunggu database -> buat tabel -> seed data awal (jika kosong)
    bootstrap()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description='''
## REST API Prototype - Merit System Personel Polri

Sistem pengelolaan data kualifikasi dan riwayat jabatan personel Polri.

### Role Pengguna
| Role | Kewenangan |
|---|---|
| ADMIN_SSDM | Full CRUD semua data + manajemen pengguna |
| OPERATOR_SATKER | CRUD personel & riwayat jabatan di satker sendiri |

### Cara Autentikasi
1. Login via POST /api/v1/auth/login
2. Copy access_token dari response
3. Klik **Authorize**, masukkan: Bearer <token>

### Akun Demo
| Username | Password | Role |
|---|---|---|
| admin.ssdm | Admin@12345 | ADMIN_SSDM |
| operator.metro | Operator@123 | OPERATOR_SATKER |
| operator.jabar | Operator@123 | OPERATOR_SATKER |
| operator.jatim | Operator@123 | OPERATOR_SATKER |
| operator.sulsel | Operator@123 | OPERATOR_SATKER |
    ''',
    version=settings.APP_VERSION,
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

PREFIX = '/api/v1'
app.include_router(auth.router, prefix=PREFIX)
app.include_router(users.router, prefix=PREFIX)
app.include_router(satker.router, prefix=PREFIX)
app.include_router(personel.router, prefix=PREFIX)
app.include_router(riwayat_jabatan.router, prefix=PREFIX)
app.include_router(dashboard.router, prefix=PREFIX)

# Web UI (login + dashboard Admin/Operator) - dilayani langsung oleh FastAPI
_STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/app', StaticFiles(directory=_STATIC_DIR, html=True), name='webapp')


@app.get('/', tags=['Root'], include_in_schema=False)
def root():
    return RedirectResponse(url='/app/')


@app.get('/health', tags=['Health Check'])
def health_check():
    return {'status': 'healthy', 'service': settings.APP_NAME, 'version': settings.APP_VERSION}
