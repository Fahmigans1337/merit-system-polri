from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.personel import PersonelCreate, PersonelUpdate, PersonelResponse
from app.schemas.riwayat_jabatan import RiwayatJabatanResponse
from app.crud import personel as crud_personel, satker as crud_satker, riwayat_jabatan as crud_rj
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix='/personel', tags=['Personel'])


def _check_access(current_user: User, satker_id: str) -> None:
    '''Pastikan user punya akses ke satker tertentu.'''
    if current_user.role == UserRole.ADMIN_SSDM:
        return
    if current_user.satker_id and str(current_user.satker_id) == str(satker_id):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Akses ditolak. Anda hanya dapat mengelola personel di satker Anda sendiri.',
    )


def _serialize_personel(p, jabatan_aktif=None) -> dict:
    return {
        'id': str(p.id),
        'nama': p.nama,
        'nrp_nip': p.nrp_nip,
        'pangkat': p.pangkat,
        'tempat_lahir': p.tempat_lahir,
        'tanggal_lahir': str(p.tanggal_lahir),
        'satker_id': str(p.satker_id),
        'satker_nama': p.satker.nama if p.satker else None,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat(),
    }


@router.get(
    '',
    response_model=dict,
    summary='List personel',
    description=(
        '**Admin SSDM**: dapat melihat semua personel dan filter per satker.\n\n'
        '**Operator Satker**: hanya melihat personel di satkernya sendiri.'
    ),
)
def list_personels(
    skip: int = Query(0, ge=0, description='Offset untuk pagination'),
    limit: int = Query(10, ge=1, le=100, description='Jumlah data per halaman (maks 100)'),
    nama: Optional[str] = Query(None, description='Filter nama personel (partial match)'),
    nrp_nip: Optional[str] = Query(None, description='Filter NRP/NIP (partial match)'),
    pangkat: Optional[str] = Query(None, description='Filter pangkat (partial match)'),
    satker_id: Optional[str] = Query(None, description='Filter satker (hanya Admin)'),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Operator wajib hanya lihat satkernya
    if current_user.role == UserRole.OPERATOR_SATKER:
        satker_id = str(current_user.satker_id) if current_user.satker_id else None

    data = crud_personel.get_personels(
        db, skip=skip, limit=limit,
        nama=nama, nrp_nip=nrp_nip, pangkat=pangkat, satker_id=satker_id,
    )
    total = crud_personel.count_personels(
        db, nama=nama, nrp_nip=nrp_nip, pangkat=pangkat, satker_id=satker_id,
    )
    return {
        'data': [_serialize_personel(p) for p in data],
        'total': total,
        'skip': skip,
        'limit': limit,
        'pages': (total + limit - 1) // limit if limit else 1,
    }


@router.post(
    '',
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary='Tambah personel baru',
)
def create_personel(
    body: PersonelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _check_access(current_user, str(body.satker_id))
    if not crud_satker.get_satker(db, str(body.satker_id)):
        raise HTTPException(404, detail='Satker tidak ditemukan')
    if crud_personel.get_personel_by_nrp(db, body.nrp_nip):
        raise HTTPException(400, detail=f"NRP/NIP '{body.nrp_nip}' sudah terdaftar dalam sistem")
    p = crud_personel.create_personel(db, body)
    # Reload dengan relasi
    p = crud_personel.get_personel(db, str(p.id))
    return {'message': 'Personel berhasil ditambahkan', 'data': _serialize_personel(p)}


@router.get(
    '/{personel_id}',
    response_model=dict,
    summary='Profil lengkap personel',
    description=(
        'Menampilkan identitas personel, jabatan aktif saat ini, '
        'dan seluruh riwayat jabatan secara kronologis dari terlama ke terbaru.'
    ),
)
def get_personel(
    personel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = crud_personel.get_personel(db, personel_id)
    if not p:
        raise HTTPException(404, detail='Personel tidak ditemukan')
    _check_access(current_user, str(p.satker_id))

    jabatan_aktif = crud_rj.get_jabatan_aktif(db, personel_id)
    riwayat = crud_rj.get_riwayat_jabatan_by_personel(db, personel_id)

    return {
        'id': str(p.id),
        'nama': p.nama,
        'nrp_nip': p.nrp_nip,
        'pangkat': p.pangkat,
        'tempat_lahir': p.tempat_lahir,
        'tanggal_lahir': str(p.tanggal_lahir),
        'satker_id': str(p.satker_id),
        'satker_nama': p.satker.nama if p.satker else None,
        'jabatan_aktif': {
            'id': str(jabatan_aktif.id),
            'jabatan': jabatan_aktif.jabatan,
            'satuan_kerja': jabatan_aktif.satuan_kerja,
            'fungsi': jabatan_aktif.fungsi,
            'tanggal_mulai': str(jabatan_aktif.tanggal_mulai),
            'nivelering_jabatan': jabatan_aktif.nivelering_jabatan,
            'status_jabatan': jabatan_aktif.status_jabatan.value,
        } if jabatan_aktif else None,
        'riwayat_jabatan': [
            {
                'id': str(rj.id),
                'jabatan': rj.jabatan,
                'satuan_kerja': rj.satuan_kerja,
                'fungsi': rj.fungsi,
                'tanggal_mulai': str(rj.tanggal_mulai),
                'tanggal_berakhir': str(rj.tanggal_berakhir) if rj.tanggal_berakhir else None,
                'nivelering_jabatan': rj.nivelering_jabatan,
                'status_jabatan': rj.status_jabatan.value,
                'keterangan': rj.keterangan,
                'created_at': rj.created_at.isoformat(),
                'updated_at': rj.updated_at.isoformat(),
            }
            for rj in riwayat
        ],
        'total_riwayat_jabatan': len(riwayat),
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat(),
    }


@router.put('/{personel_id}', response_model=dict, summary='Update data personel')
def update_personel(
    personel_id: str,
    body: PersonelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = crud_personel.get_personel(db, personel_id)
    if not p:
        raise HTTPException(404, detail='Personel tidak ditemukan')
    _check_access(current_user, str(p.satker_id))
    if body.satker_id:
        _check_access(current_user, str(body.satker_id))
        if not crud_satker.get_satker(db, str(body.satker_id)):
            raise HTTPException(404, detail='Satker tujuan tidak ditemukan')
    updated = crud_personel.update_personel(db, p, body)
    updated = crud_personel.get_personel(db, personel_id)
    return {'message': 'Personel berhasil diperbarui', 'data': _serialize_personel(updated)}


@router.delete(
    '/{personel_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Hapus personel',
    description='Menghapus personel beserta seluruh riwayat jabatannya (cascade delete).',
)
def delete_personel(
    personel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    p = crud_personel.get_personel(db, personel_id)
    if not p:
        raise HTTPException(404, detail='Personel tidak ditemukan')
    _check_access(current_user, str(p.satker_id))
    crud_personel.delete_personel(db, p)
