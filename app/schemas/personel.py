from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime, date


class PersonelBase(BaseModel):
    nama: str
    nrp_nip: str
    pangkat: str
    tempat_lahir: str
    tanggal_lahir: date
    satker_id: UUID

    @field_validator('nama', 'pangkat', 'tempat_lahir')
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Field tidak boleh kosong')
        return v

    @field_validator('nrp_nip')
    @classmethod
    def nrp_nip_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('NRP/NIP tidak boleh kosong')
        cleaned = v.replace(' ', '').replace('-', '')
        if not cleaned.isalnum():
            raise ValueError('NRP/NIP hanya boleh berisi huruf, angka, spasi, dan tanda hubung')
        return v

    @field_validator('tanggal_lahir')
    @classmethod
    def tanggal_lahir_valid(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError('Tanggal lahir harus lebih awal dari hari ini')
        return v


class PersonelCreate(PersonelBase):
    pass


class PersonelUpdate(BaseModel):
    nama: Optional[str] = None
    pangkat: Optional[str] = None
    tempat_lahir: Optional[str] = None
    tanggal_lahir: Optional[date] = None
    satker_id: Optional[UUID] = None

    @field_validator('nama', 'pangkat', 'tempat_lahir')
    @classmethod
    def not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Field tidak boleh kosong')
        return v


class PersonelResponse(BaseModel):
    id: UUID
    nama: str
    nrp_nip: str
    pangkat: str
    tempat_lahir: str
    tanggal_lahir: date
    satker_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
