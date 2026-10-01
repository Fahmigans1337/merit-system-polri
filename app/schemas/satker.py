from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class SatkerBase(BaseModel):
    nama: str
    kode: str
    deskripsi: Optional[str] = None

    @field_validator('nama')
    @classmethod
    def nama_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Nama satker tidak boleh kosong')
        return v

    @field_validator('kode')
    @classmethod
    def kode_valid(cls, v: str) -> str:
        v = v.strip().upper()
        if not v:
            raise ValueError('Kode satker tidak boleh kosong')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Kode satker hanya boleh berisi huruf, angka, dash, dan underscore')
        return v


class SatkerCreate(SatkerBase):
    pass


class SatkerUpdate(BaseModel):
    nama: Optional[str] = None
    kode: Optional[str] = None
    deskripsi: Optional[str] = None


class SatkerResponse(BaseModel):
    id: UUID
    nama: str
    kode: str
    deskripsi: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
