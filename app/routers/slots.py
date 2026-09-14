from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api", tags=["Delivery Slots"])

@router.get("/slots", response_model=List[schemas.SlotOut])
def list_slots(
    target_date: Optional[str] = Query(None, description="Filter slots by date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    return crud.get_slots(db, target_date=target_date)
