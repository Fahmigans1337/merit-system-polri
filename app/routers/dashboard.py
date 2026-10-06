from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.personel import Personel
from app.models.satker import Satker
from app.models.riwayat_jabatan import RiwayatJabatan, StatusJabatan

router = APIRouter(prefix='/dashboard', tags=['Dashboard'])


@router.get(
    '/stats',
    summary='Statistik dashboard',
    description=(
        '**Admin SSDM**: statistik seluruh satker.\n\n'
        '**Operator Satker**: statistik hanya untuk satker sendiri.'
    ),
)
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_admin = current_user.role == UserRole.ADMIN_SSDM
    scope_satker = None if is_admin else (
        str(current_user.satker_id) if current_user.satker_id else '__none__'
    )

    pq = db.query(Personel)
    if scope_satker:
        pq = pq.filter(Personel.satker_id == scope_satker)
    total_personel = pq.count()

    rj_q = db.query(RiwayatJabatan).join(Personel, Personel.id == RiwayatJabatan.personel_id)
    if scope_satker:
        rj_q = rj_q.filter(Personel.satker_id == scope_satker)
    total_riwayat = rj_q.count()
    jabatan_aktif = rj_q.filter(RiwayatJabatan.status_jabatan == StatusJabatan.AKTIF).count()

    # personel per pangkat
    pangkat_q = db.query(Personel.pangkat, func.count(Personel.id))
    if scope_satker:
        pangkat_q = pangkat_q.filter(Personel.satker_id == scope_satker)
    per_pangkat = [
        {'pangkat': p, 'total': t}
        for p, t in pangkat_q.group_by(Personel.pangkat).order_by(func.count(Personel.id).desc()).all()
    ]

    # personel per satker (admin: semua, operator: satkernya saja)
    satker_q = (
        db.query(Satker.id, Satker.nama, Satker.kode, func.count(Personel.id))
        .outerjoin(Personel, Personel.satker_id == Satker.id)
    )
    if scope_satker:
        satker_q = satker_q.filter(Satker.id == scope_satker)
    per_satker = [
        {'id': str(i), 'nama': n, 'kode': k, 'total': t}
        for i, n, k, t in satker_q.group_by(Satker.id, Satker.nama, Satker.kode)
        .order_by(func.count(Personel.id).desc()).all()
    ]

    # personel terbaru
    recent_q = db.query(Personel)
    if scope_satker:
        recent_q = recent_q.filter(Personel.satker_id == scope_satker)
    recent = [
        {
            'id': str(p.id),
            'nama': p.nama,
            'nrp_nip': p.nrp_nip,
            'pangkat': p.pangkat,
            'satker_nama': p.satker.nama if p.satker else None,
        }
        for p in recent_q.order_by(Personel.created_at.desc()).limit(5).all()
    ]

    result = {
        'scope': 'ALL' if is_admin else 'SATKER',
        'total_personel': total_personel,
        'total_riwayat_jabatan': total_riwayat,
        'jabatan_aktif': jabatan_aktif,
        'per_pangkat': per_pangkat,
        'per_satker': per_satker,
        'personel_terbaru': recent,
    }
    if is_admin:
        result['total_satker'] = db.query(Satker).count()
        result['total_user'] = db.query(User).count()
    return result
