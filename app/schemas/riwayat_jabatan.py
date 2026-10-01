from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from app.models.riwayat_jabatan import StatusJabatan


class RiwayatJabatanBase(BaseModel):
    jabatan: str
    satuan_kerja: str
    fungsi: str
    tanggal_mulai: date
    tanggal_berakhir: Optional[date] = None
    nivelering_jabatan: str
    status_jabatan: StatusJabatan = StatusJabatan.AKTIF
    keterangan: Optional[str] = None

    @field_validator('jabatan', 'satuan_kerja', 'fungsi', 'nivelering_jabatan')
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Field tidak boleh kosong')
        return v

    @model_validator(mode='after')
    def validate_tanggal(self) -> 'RiwayatJabatanBase':
        if self.tanggal_berakhir and self.tanggal_mulai:
            if self.tanggal_berakhir < self.tanggal_mulai:
                raise ValueError('tanggal_berakhir tidak boleh sebelum tanggal_mulai')
        return self


class RiwayatJabatanCreate(RiwayatJabatanBase):
    pass


class RiwayatJabatanUpdate(BaseModel):
    jabatan: Optional[str] = None
    satuan_kerja: Optional[str] = None
    fungsi: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_berakhir: Optional[date] = None
    nivelering_jabatan: Optional[str] = None
    status_jabatan: Optional[StatusJabatan] = None
    keterangan: Optional[str] = None


class RiwayatJabatanResponse(BaseModel):
    id: UUID
    personel_id: UUID
    jabatan: str
    satuan_kerja: str
    fungsi: str
    tanggal_mulai: date
    tanggal_berakhir: Optional[date]
    nivelering_jabatan: str
    status_jabatan: StatusJabatan
    keterangan: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
