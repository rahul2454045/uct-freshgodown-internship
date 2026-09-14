from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/api", tags=["Products & Categories"])

@router.get("/categories", response_model=List[schemas.CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@router.get("/products", response_model=List[schemas.ProductOut])
def list_products(
    category_id: Optional[int] = Query(None, description="Filter by Category ID"),
    search: Optional[str] = Query(None, description="Search product name or description"),
    in_stock_only: bool = Query(False, description="Show only in-stock items"),
    sort_by: Optional[str] = Query("popular", description="Sort by: popular, price_asc, price_desc, rating"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return crud.get_products(
        db,
        category_id=category_id,
        search=search,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )

@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    prod = crud.get_product_by_id(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": prod.id,
        "name": prod.name,
        "slug": prod.slug,
        "category_id": prod.category_id,
        "category_name": prod.category.name if prod.category else None,
        "description": prod.description,
        "unit": prod.unit,
        "price": prod.price,
        "mrp": prod.mrp,
        "stock_quantity": prod.stock_quantity,
        "low_stock_threshold": prod.low_stock_threshold,
        "is_available": prod.is_available,
        "image_url": prod.image_url,
        "badge": prod.badge,
        "rating": prod.rating,
        "review_count": prod.review_count,
        "created_at": prod.created_at
    }

@router.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_new_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    prod = crud.create_product(db, product_in)
    return {
        "id": prod.id,
        "name": prod.name,
        "slug": prod.slug,
        "category_id": prod.category_id,
        "category_name": prod.category.name if prod.category else None,
        "description": prod.description,
        "unit": prod.unit,
        "price": prod.price,
        "mrp": prod.mrp,
        "stock_quantity": prod.stock_quantity,
        "low_stock_threshold": prod.low_stock_threshold,
        "is_available": prod.is_available,
        "image_url": prod.image_url,
        "badge": prod.badge,
        "rating": prod.rating,
        "review_count": prod.review_count,
        "created_at": prod.created_at
    }

@router.patch("/products/{product_id}/stock", response_model=schemas.ProductOut)
def update_stock(product_id: int, quantity: int = Query(..., ge=0), db: Session = Depends(get_db)):
    updated = crud.update_product_stock(db, product_id, quantity)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return {
        "id": updated.id,
        "name": updated.name,
        "slug": updated.slug,
        "category_id": updated.category_id,
        "category_name": updated.category.name if updated.category else None,
        "description": updated.description,
        "unit": updated.unit,
        "price": updated.price,
        "mrp": updated.mrp,
        "stock_quantity": updated.stock_quantity,
        "low_stock_threshold": updated.low_stock_threshold,
        "is_available": updated.is_available,
        "image_url": updated.image_url,
        "badge": updated.badge,
        "rating": updated.rating,
        "review_count": updated.review_count,
        "created_at": updated.created_at
    }
