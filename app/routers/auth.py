from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.schemas.auth import Token, LoginRequest, RefreshTokenRequest
from app.schemas.user import UserResponse
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.core.dependencies import get_current_user
from app.crud import user as crud_user

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post(
    '/login',
    response_model=Token,
    summary='Login pengguna',
    description='Login dengan username dan password. Mengembalikan JWT access token (1 hari) dan refresh token (7 hari).',
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Username atau password salah',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Akun tidak aktif. Hubungi Admin SSDM.')

    access_token = create_access_token({'sub': str(user.id)})
    refresh_token = create_refresh_token({'sub': str(user.id)})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    '/refresh',
    response_model=Token,
    summary='Refresh access token',
    description='Gunakan refresh token untuk mendapatkan access token baru tanpa login ulang.',
)
def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    exc = HTTPException(status_code=401, detail='Refresh token tidak valid atau sudah kadaluarsa')
    try:
        payload = decode_token(body.refresh_token)
        user_id: str = payload.get('sub')
        if not user_id or payload.get('type') != 'refresh':
            raise exc
    except JWTError:
        raise exc

    user = crud_user.get_user(db, user_id)
    if not user or not user.is_active:
        raise exc

    access_token = create_access_token({'sub': str(user.id)})
    new_refresh = create_refresh_token({'sub': str(user.id)})
    return Token(access_token=access_token, refresh_token=new_refresh)


@router.get(
    '/me',
    response_model=UserResponse,
    summary='Info pengguna aktif',
    description='Mengembalikan data pengguna yang sedang login berdasarkan token.',
)
def get_me(current_user=Depends(get_current_user)):
    return current_user
