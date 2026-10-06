from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.riwayat_jabatan import (
    RiwayatJabatanCreate,
    RiwayatJabatanUpdate,
    RiwayatJabatanResponse,
)
from app.crud import personel as crud_personel, riwayat_jabatan as crud_rj
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole

router = APIRouter(
    prefix='/personel/{personel_id}/riwayat-jabatan',
    tags=['Riwayat Jabatan'],
)


def _get_personel_or_404(db: Session, personel_id: str, current_user: User):
    '''Ambil personel dan validasi akses user.'''
    p = crud_personel.get_personel(db, personel_id)
    if not p:
        raise HTTPException(404, detail='Personel tidak ditemukan')
    if current_user.role == UserRole.OPERATOR_SATKER:
        if not current_user.satker_id or str(current_user.satker_id) != str(p.satker_id):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail='Akses ditolak. Personel berada di luar satker Anda.',
            )
    return p


@router.get(
    '',
    response_model=List[RiwayatJabatanResponse],
    summary='List riwayat jabatan',
    description='Menampilkan seluruh riwayat jabatan personel secara **kronologis** (terlama → terbaru).',
)
def list_riwayat(
    personel_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_personel_or_404(db, personel_id, current_user)
    return crud_rj.get_riwayat_jabatan_by_personel(db, personel_id, skip=skip, limit=limit)


@router.post(
    '',
    response_model=RiwayatJabatanResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Tambah riwayat jabatan',
)
def create_riwayat(
    personel_id: str,
    body: RiwayatJabatanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    '''Menambahkan satu entri riwayat jabatan baru untuk personel.'''
    _get_personel_or_404(db, personel_id, current_user)
    return crud_rj.create_riwayat_jabatan(db, body, personel_id)


@router.get(
    '/{rj_id}',
    response_model=RiwayatJabatanResponse,
    summary='Detail riwayat jabatan',
)
def get_riwayat(
    personel_id: str,
    rj_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_personel_or_404(db, personel_id, current_user)
    rj = crud_rj.get_riwayat_jabatan(db, rj_id)
    if not rj or str(rj.personel_id) != personel_id:
        raise HTTPException(404, detail='Riwayat jabatan tidak ditemukan')
    return rj


@router.put(
    '/{rj_id}',
    response_model=RiwayatJabatanResponse,
    summary='Update riwayat jabatan',
)
def update_riwayat(
    personel_id: str,
    rj_id: str,
    body: RiwayatJabatanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_personel_or_404(db, personel_id, current_user)
    rj = crud_rj.get_riwayat_jabatan(db, rj_id)
    if not rj or str(rj.personel_id) != personel_id:
        raise HTTPException(404, detail='Riwayat jabatan tidak ditemukan')

    # Cross-validate tanggal jika keduanya berubah
    tgl_mulai = body.tanggal_mulai or rj.tanggal_mulai
    tgl_berakhir = body.tanggal_berakhir if body.tanggal_berakhir is not None else rj.tanggal_berakhir
    if tgl_berakhir and tgl_berakhir < tgl_mulai:
        raise HTTPException(400, detail='tanggal_berakhir tidak boleh sebelum tanggal_mulai')

    return crud_rj.update_riwayat_jabatan(db, rj, body)


@router.delete(
    '/{rj_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Hapus riwayat jabatan',
)
def delete_riwayat(
    personel_id: str,
    rj_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_personel_or_404(db, personel_id, current_user)
    rj = crud_rj.get_riwayat_jabatan(db, rj_id)
    if not rj or str(rj.personel_id) != personel_id:
        raise HTTPException(404, detail='Riwayat jabatan tidak ditemukan')
    crud_rj.delete_riwayat_jabatan(db, rj)
