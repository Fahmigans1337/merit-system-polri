import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class StatusJabatan(str, enum.Enum):
    AKTIF = 'AKTIF'
    NON_AKTIF = 'NON_AKTIF'


class RiwayatJabatan(Base):
    __tablename__ = 'riwayat_jabatan'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personel_id = Column(
        String(36),
        ForeignKey('personel.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    jabatan = Column(String(200), nullable=False)
    satuan_kerja = Column(String(200), nullable=False)
    fungsi = Column(String(200), nullable=False)
    tanggal_mulai = Column(Date, nullable=False)
    tanggal_berakhir = Column(Date, nullable=True)
    nivelering_jabatan = Column(String(100), nullable=False)
    status_jabatan = Column(Enum(StatusJabatan), nullable=False, default=StatusJabatan.AKTIF)
    keterangan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    personel = relationship('Personel', back_populates='riwayat_jabatan')
