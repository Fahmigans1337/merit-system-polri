from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud import user as crud_user, satker as crud_satker
from app.core.dependencies import get_admin_user
from app.models.user import User

router = APIRouter(prefix='/users', tags=['User Management (Admin Only)'])


@router.get('', response_model=List[UserResponse], summary='List semua pengguna')
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    '''Daftar semua pengguna sistem. **Hanya Admin SSDM.**'''
    return crud_user.get_users(db, skip=skip, limit=limit)


@router.post(
    '',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Buat pengguna baru',
)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    '''Membuat akun pengguna baru (Admin atau Operator). **Hanya Admin SSDM.**'''
    if crud_user.get_user_by_username(db, body.username):
        raise HTTPException(400, detail='Username sudah digunakan')
    if crud_user.get_user_by_email(db, body.email):
        raise HTTPException(400, detail='Email sudah digunakan')
    if body.satker_id and not crud_satker.get_satker(db, str(body.satker_id)):
        raise HTTPException(404, detail='Satker tidak ditemukan')
    return crud_user.create_user(db, body)


@router.get('/{user_id}', response_model=UserResponse, summary='Detail pengguna')
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    '''Detail pengguna berdasarkan ID. **Hanya Admin SSDM.**'''
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(404, detail='Pengguna tidak ditemukan')
    return user


@router.put('/{user_id}', response_model=UserResponse, summary='Update pengguna')
def update_user(
    user_id: str,
    body: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    '''Update data pengguna. **Hanya Admin SSDM.**'''
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(404, detail='Pengguna tidak ditemukan')
    if body.email and body.email != user.email:
        if crud_user.get_user_by_email(db, body.email):
            raise HTTPException(400, detail='Email sudah digunakan')
    if body.satker_id and not crud_satker.get_satker(db, str(body.satker_id)):
        raise HTTPException(404, detail='Satker tidak ditemukan')
    return crud_user.update_user(db, user, body)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Hapus pengguna')
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    '''Hapus pengguna. Tidak bisa menghapus akun sendiri. **Hanya Admin SSDM.**'''
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(404, detail='Pengguna tidak ditemukan')
    if str(user.id) == str(current_user.id):
        raise HTTPException(400, detail='Tidak dapat menghapus akun sendiri yang sedang aktif')
    crud_user.delete_user(db, user)
