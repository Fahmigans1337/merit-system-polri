from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    '''Dependency: decode JWT, return authenticated User.'''
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Token tidak valid atau sudah kadaluarsa',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get('sub')
        token_type: str = payload.get('type')
        if not user_id or token_type != 'access':
            raise exc
    except JWTError:
        raise exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise exc
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Akun tidak aktif')
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    '''Dependency: hanya Admin SSDM yang bisa lanjut.'''
    if current_user.role != UserRole.ADMIN_SSDM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Akses ditolak. Fitur ini hanya untuk Admin SSDM.',
        )
    return current_user
