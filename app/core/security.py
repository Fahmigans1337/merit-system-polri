from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt
from app.config import settings


# ── Password Hashing (bcrypt langsung, kompatibel semua versi) ──────────────


def hash_password(password: str) -> str:
    '''Hash password menggunakan bcrypt.'''
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    '''Verifikasi password terhadap hash bcrypt.'''
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


# ── JWT Token ────────────────────────────────────────────────────────────────


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    '''Buat JWT access token (default expire: 24 jam).'''
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({'exp': expire, 'type': 'access'})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    '''Buat JWT refresh token (default expire: 7 hari).'''
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({'exp': expire, 'type': 'refresh'})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    '''Decode dan verifikasi JWT token. Raise JWTError jika invalid.'''
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
