import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Personel(Base):
    __tablename__ = 'personel'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nama = Column(String(200), nullable=False)
    nrp_nip = Column(String(50), unique=True, nullable=False, index=True)
    pangkat = Column(String(100), nullable=False)
    tempat_lahir = Column(String(100), nullable=False)
    tanggal_lahir = Column(Date, nullable=False)
    satker_id = Column(String(36), ForeignKey('satker.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    satker = relationship('Satker', back_populates='personel')
    riwayat_jabatan = relationship(
        'RiwayatJabatan',
        back_populates='personel',
        order_by='RiwayatJabatan.tanggal_mulai',
        cascade='all, delete-orphan',
    )
