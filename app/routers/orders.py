import math
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud
from app.config import GODOWN_LAT, GODOWN_LNG

router = APIRouter(prefix="/api", tags=["Orders & Tracking"])

@router.post("/orders", response_model=schemas.OrderOut, status_code=201)
def place_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        order = crud.create_order(db, order_in)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_number}", response_model=schemas.OrderOut)
def get_order(order_number: str, db: Session = Depends(get_db)):
    order = crud.get_order_by_number(db, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/orders/{order_number}/tracking")
def get_order_tracking(order_number: str, db: Session = Depends(get_db)):
    order = crud.get_order_by_number(db, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Destination lat/lng (simulated within ~5 km of godown hub)
    offset_lat = ((order.id * 37) % 50 - 25) / 1000.0
    offset_lng = ((order.id * 59) % 50 - 25) / 1000.0
    customer_lat = GODOWN_LAT + offset_lat + 0.025
    customer_lng = GODOWN_LNG + offset_lng + 0.020

    # Ensure timezone-aware comparison
    created_at = order.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    elapsed_seconds = (datetime.now(timezone.utc) - created_at).total_seconds()
    
    # Simulation progress:
    if order.order_status in ["PLACED", "PICKED_FROM_GODOWN"]:
        progress = 0.05
        eta_minutes = 45
    elif order.order_status == "PACKED":
        progress = 0.15
        eta_minutes = 35
    elif order.order_status == "OUT_FOR_DELIVERY":
        simulated_step = min(0.95, 0.2 + (elapsed_seconds / 120.0) * 0.7)
        progress = simulated_step
        eta_minutes = max(3, int(order.est_eta_minutes * (1 - progress)))
    elif order.order_status == "DELIVERED":
        progress = 1.0
        eta_minutes = 0
    else:
        progress = 0.0
        eta_minutes = 0

    current_lat = GODOWN_LAT + (customer_lat - GODOWN_LAT) * progress
    current_lng = GODOWN_LNG + (customer_lng - GODOWN_LNG) * progress

    milestones = [
        {
            "step": "PLACED",
            "title": "Order Placed & Confirmed",
            "description": f"Received at {order.created_at.strftime('%H:%M')}. Godown inventory reserved.",
            "completed": True,
            "active": order.order_status == "PLACED"
        },
        {
            "step": "PICKED_FROM_GODOWN",
            "title": "Items Picked from Godown",
            "description": "Store picker has gathered your items from central godown bays.",
            "completed": order.order_status in ["PICKED_FROM_GODOWN", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED"],
            "active": order.order_status == "PICKED_FROM_GODOWN"
        },
        {
            "step": "PACKED",
            "title": "Quality Checked & Packed",
            "description": "Packed in eco-friendly insulated bags with temperature control.",
            "completed": order.order_status in ["PACKED", "OUT_FOR_DELIVERY", "DELIVERED"],
            "active": order.order_status == "PACKED"
        },
        {
            "step": "OUT_FOR_DELIVERY",
            "title": "Out for Delivery",
            "description": f"Assigned to {order.driver_name}. Moving towards your address.",
            "completed": order.order_status in ["OUT_FOR_DELIVERY", "DELIVERED"],
            "active": order.order_status == "OUT_FOR_DELIVERY"
        },
        {
            "step": "DELIVERED",
            "title": "Delivered to Doorstep",
            "description": f"Delivered within slot: {order.slot_window}.",
            "completed": order.order_status == "DELIVERED",
            "active": order.order_status == "DELIVERED"
        }
    ]

    return {
        "order_number": order.order_number,
        "status": order.order_status,
        "eta_minutes": eta_minutes,
        "slot_date": order.slot_date,
        "slot_window": order.slot_window,
        "customer": {
            "name": order.customer_name,
            "address": order.delivery_address,
            "city": order.delivery_city,
            "lat": customer_lat,
            "lng": customer_lng
        },
        "godown": {
            "name": "Central Godown & Fulfillment Hub #4",
            "lat": GODOWN_LAT,
            "lng": GODOWN_LNG
        },
        "driver": {
            "name": order.driver_name,
            "phone": order.driver_phone,
            "lat": current_lat,
            "lng": current_lng,
            "vehicle": "Electric Cargo Delivery Van (EV-04)"
        },
        "progress_percent": round(progress * 100, 1),
        "milestones": milestones,
        "items_count": len(order.items),
        "total_amount": order.total_amount
    }
