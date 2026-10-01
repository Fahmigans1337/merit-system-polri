from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.personel import Personel
from app.schemas.personel import PersonelCreate, PersonelUpdate


def get_personel(db: Session, personel_id: str) -> Optional[Personel]:
    return (
        db.query(Personel)
        .options(joinedload(Personel.satker), joinedload(Personel.riwayat_jabatan))
        .filter(Personel.id == personel_id)
        .first()
    )


def get_personel_by_nrp(db: Session, nrp_nip: str) -> Optional[Personel]:
    return db.query(Personel).filter(Personel.nrp_nip == nrp_nip).first()


def get_personels(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    nama: Optional[str] = None,
    nrp_nip: Optional[str] = None,
    pangkat: Optional[str] = None,
    satker_id: Optional[str] = None,
) -> List[Personel]:
    q = db.query(Personel).options(joinedload(Personel.satker))
    if nama:
        q = q.filter(Personel.nama.ilike(f'%{nama}%'))
    if nrp_nip:
        q = q.filter(Personel.nrp_nip.ilike(f'%{nrp_nip}%'))
    if pangkat:
        q = q.filter(Personel.pangkat.ilike(f'%{pangkat}%'))
    if satker_id:
        q = q.filter(Personel.satker_id == satker_id)
    return q.order_by(Personel.nama).offset(skip).limit(limit).all()


def count_personels(
    db: Session,
    nama: Optional[str] = None,
    nrp_nip: Optional[str] = None,
    pangkat: Optional[str] = None,
    satker_id: Optional[str] = None,
) -> int:
    q = db.query(Personel)
    if nama:
        q = q.filter(Personel.nama.ilike(f'%{nama}%'))
    if nrp_nip:
        q = q.filter(Personel.nrp_nip.ilike(f'%{nrp_nip}%'))
    if pangkat:
        q = q.filter(Personel.pangkat.ilike(f'%{pangkat}%'))
    if satker_id:
        q = q.filter(Personel.satker_id == satker_id)
    return q.count()


def create_personel(db: Session, personel: PersonelCreate) -> Personel:
    db_p = Personel(**personel.model_dump())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p


def update_personel(db: Session, personel: Personel, data: PersonelUpdate) -> Personel:
    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(personel, field, value)
    db.commit()
    db.refresh(personel)
    return personel


def delete_personel(db: Session, personel: Personel) -> None:
    db.delete(personel)
    db.commit()
