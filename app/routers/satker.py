from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.satker import SatkerCreate, SatkerUpdate, SatkerResponse
from app.crud import satker as crud_satker
from app.core.dependencies import get_admin_user, get_current_user
from app.models.user import User

router = APIRouter(prefix='/satker', tags=['Satuan Kerja'])


@router.get('', summary='List semua satuan kerja')
def list_satkers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    data = crud_satker.get_satkers(db, skip=skip, limit=limit)
    total = crud_satker.count_satkers(db)
    return {
        'data': [SatkerResponse.model_validate(s).model_dump() for s in data],
        'total': total,
        'skip': skip,
        'limit': limit,
    }


@router.post('', response_model=SatkerResponse, status_code=status.HTTP_201_CREATED, summary='Tambah satker baru')
def create_satker(body: SatkerCreate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    if crud_satker.get_satker_by_kode(db, body.kode):
        raise HTTPException(400, detail=f"Satker kode '{body.kode}' sudah ada")
    return crud_satker.create_satker(db, body)


@router.get('/{satker_id}', response_model=SatkerResponse, summary='Detail satker')
def get_satker(satker_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    satker = crud_satker.get_satker(db, satker_id)
    if not satker:
        raise HTTPException(404, detail='Satker tidak ditemukan')
    return satker


@router.put('/{satker_id}', response_model=SatkerResponse, summary='Update satker')
def update_satker(satker_id: str, body: SatkerUpdate, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    satker = crud_satker.get_satker(db, satker_id)
    if not satker:
        raise HTTPException(404, detail='Satker tidak ditemukan')
    if body.kode and body.kode.upper() != satker.kode:
        if crud_satker.get_satker_by_kode(db, body.kode):
            raise HTTPException(400, detail=f"Kode '{body.kode.upper()}' sudah dipakai")
    return crud_satker.update_satker(db, satker, body)


@router.delete('/{satker_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Hapus satker')
def delete_satker(satker_id: str, db: Session = Depends(get_db), _: User = Depends(get_admin_user)):
    satker = crud_satker.get_satker(db, satker_id)
    if not satker:
        raise HTTPException(404, detail='Satker tidak ditemukan')
    try:
        crud_satker.delete_satker(db, satker)
    except Exception:
        raise HTTPException(400, detail='Satker tidak bisa dihapus, masih ada data terkait')
