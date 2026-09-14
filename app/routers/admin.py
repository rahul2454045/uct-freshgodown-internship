from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud, models

router = APIRouter(prefix="/api/admin", tags=["Godown Manager & Admin Portal"])

@router.get("/stats", response_model=schemas.AdminStatsOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_admin_stats(db)

@router.get("/orders", response_model=List[schemas.OrderOut])
def get_all_orders(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_orders(db, limit=limit)

@router.patch("/orders/{order_id}/status", response_model=schemas.OrderOut)
def update_fulfillment_status(
    order_id: int,
    status_in: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db)
):
    updated = crud.update_order_status(db, order_id, status_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated

@router.get("/inventory")
def get_godown_inventory(db: Session = Depends(get_db)):
    products = db.query(models.Product).order_by(models.Product.stock_quantity.asc()).all()
    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "category": p.category.name if p.category else "Uncategorized",
            "unit": p.unit,
            "price": p.price,
            "mrp": p.mrp,
            "stock_quantity": p.stock_quantity,
            "low_stock_threshold": p.low_stock_threshold,
            "is_low_stock": p.stock_quantity <= p.low_stock_threshold,
            "is_available": p.is_available,
            "badge": p.badge
        })
    return result

@router.post("/inventory/{product_id}/restock")
def restock_product(
    product_id: int,
    add_quantity: int = Query(..., ge=1, description="Quantity to add to godown stock"),
    db: Session = Depends(get_db)
):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    prod.stock_quantity += add_quantity
    prod.is_available = True
    db.commit()
    db.refresh(prod)
    return {
        "message": f"Successfully restocked {prod.name}",
        "new_stock": prod.stock_quantity,
        "is_available": prod.is_available
    }
