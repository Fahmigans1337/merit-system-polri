from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.satker import Satker
from app.schemas.satker import SatkerCreate, SatkerUpdate


def get_satker(db: Session, satker_id: str) -> Optional[Satker]:
    return db.query(Satker).filter(Satker.id == satker_id).first()


def get_satker_by_kode(db: Session, kode: str) -> Optional[Satker]:
    return db.query(Satker).filter(Satker.kode == kode.upper()).first()


def get_satkers(db: Session, skip: int = 0, limit: int = 100) -> List[Satker]:
    return db.query(Satker).order_by(Satker.nama).offset(skip).limit(limit).all()


def count_satkers(db: Session) -> int:
    return db.query(Satker).count()


def create_satker(db: Session, satker: SatkerCreate) -> Satker:
    db_satker = Satker(**satker.model_dump())
    db.add(db_satker)
    db.commit()
    db.refresh(db_satker)
    return db_satker


def update_satker(db: Session, satker: Satker, data: SatkerUpdate) -> Satker:
    update_dict = data.model_dump(exclude_unset=True)
    if 'kode' in update_dict and update_dict['kode']:
        update_dict['kode'] = update_dict['kode'].upper()
    for field, value in update_dict.items():
        setattr(satker, field, value)
    db.commit()
    db.refresh(satker)
    return satker


def delete_satker(db: Session, satker: Satker) -> None:
    db.delete(satker)
    db.commit()
