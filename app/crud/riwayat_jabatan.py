from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.riwayat_jabatan import RiwayatJabatan, StatusJabatan
from app.schemas.riwayat_jabatan import RiwayatJabatanCreate, RiwayatJabatanUpdate


def get_riwayat_jabatan(db: Session, rj_id: str) -> Optional[RiwayatJabatan]:
    return db.query(RiwayatJabatan).filter(RiwayatJabatan.id == rj_id).first()


def get_riwayat_jabatan_by_personel(
    db: Session, personel_id: str, skip: int = 0, limit: int = 100
) -> List[RiwayatJabatan]:
    return (
        db.query(RiwayatJabatan)
        .filter(RiwayatJabatan.personel_id == personel_id)
        .order_by(RiwayatJabatan.tanggal_mulai.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_jabatan_aktif(db: Session, personel_id: str) -> Optional[RiwayatJabatan]:
    return (
        db.query(RiwayatJabatan)
        .filter(
            RiwayatJabatan.personel_id == personel_id,
            RiwayatJabatan.status_jabatan == StatusJabatan.AKTIF,
        )
        .order_by(RiwayatJabatan.tanggal_mulai.desc())
        .first()
    )


def create_riwayat_jabatan(
    db: Session, rj: RiwayatJabatanCreate, personel_id: str
) -> RiwayatJabatan:
    db_rj = RiwayatJabatan(**rj.model_dump(), personel_id=personel_id)
    db.add(db_rj)
    db.commit()
    db.refresh(db_rj)
    return db_rj


def update_riwayat_jabatan(
    db: Session, rj: RiwayatJabatan, data: RiwayatJabatanUpdate
) -> RiwayatJabatan:
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(rj, field, value)
    db.commit()
    db.refresh(rj)
    return rj


def delete_riwayat_jabatan(db: Session, rj: RiwayatJabatan) -> None:
    db.delete(rj)
    db.commit()
