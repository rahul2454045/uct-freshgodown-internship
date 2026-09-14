import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app import models, schemas
from app.config import MIN_ORDER_FREE_DELIVERY, STANDARD_DELIVERY_FEE, TAX_RATE, GODOWN_LAT, GODOWN_LNG

# ================= CATEGORY OPERATIONS =================
def get_categories(db: Session):
    cats = db.query(models.Category).order_by(models.Category.display_order).all()
    result = []
    for c in cats:
        count = db.query(models.Product).filter(models.Product.category_id == c.id).count()
        result.append({
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "icon": c.icon,
            "display_order": c.display_order,
            "product_count": count
        })
    return result

def get_category_by_id(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()


# ================= PRODUCT OPERATIONS =================
def get_products(
    db: Session,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    in_stock_only: bool = False,
    sort_by: Optional[str] = "popular", # "price_asc", "price_desc", "rating", "popular"
    limit: int = 100,
    offset: int = 0
):
    query = db.query(models.Product)
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
        
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(search_fmt),
                models.Product.description.ilike(search_fmt)
            )
        )
        
    if in_stock_only:
        query = query.filter(models.Product.stock_quantity > 0, models.Product.is_available == True)
        
    if sort_by == "price_asc":
        query = query.order_by(models.Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(models.Product.price.desc())
    elif sort_by == "rating":
        query = query.order_by(models.Product.rating.desc())
    else:
        query = query.order_by(models.Product.id.asc())

    products = query.offset(offset).limit(limit).all()
    
    result = []
    for p in products:
        p_dict = {
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "category_id": p.category_id,
            "category_name": p.category.name if p.category else None,
            "description": p.description,
            "unit": p.unit,
            "price": p.price,
            "mrp": p.mrp,
            "stock_quantity": p.stock_quantity,
            "low_stock_threshold": p.low_stock_threshold,
            "is_available": p.is_available,
            "image_url": p.image_url,
            "badge": p.badge,
            "rating": p.rating,
            "review_count": p.review_count,
            "created_at": p.created_at
        }
        result.append(p_dict)
    return result

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_product(db: Session, product_in: schemas.ProductCreate):
    db_prod = models.Product(**product_in.model_dump())
    db.add(db_prod)
    db.commit()
    db.refresh(db_prod)
    return db_prod

def update_product_stock(db: Session, product_id: int, new_quantity: int):
    prod = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not prod:
        return None
    prod.stock_quantity = new_quantity
    prod.is_available = new_quantity > 0
    db.commit()
    db.refresh(prod)
    return prod


# ================= DELIVERY SLOTS =================
def ensure_default_slots(db: Session):
    """Generate delivery slots for Today, Tomorrow, and Day After Tomorrow if not present."""
    today = date.today()
    standard_windows = [
        ("06:00 AM - 08:00 AM", "Early Morning Slot"),
        ("09:00 AM - 11:00 AM", "Morning Rush Slot"),
        ("02:00 PM - 04:00 PM", "Afternoon Express"),
        ("07:00 PM - 09:00 PM", "Evening Prime Slot")
    ]
    
    for offset in range(3):
        day = today + timedelta(days=offset)
        day_str = day.isoformat()
        
        for window, label in standard_windows:
            exists = db.query(models.DeliverySlot).filter(
                models.DeliverySlot.slot_date == day_str,
                models.DeliverySlot.time_window == window
            ).first()
            if not exists:
                slot = models.DeliverySlot(
                    slot_date=day_str,
                    time_window=window,
                    slot_label=label,
                    max_capacity=15,
                    booked_count=offset * 2, # realistic initial booked counts
                    is_active=True
                )
                db.add(slot)
    db.commit()

def get_slots(db: Session, target_date: Optional[str] = None):
    ensure_default_slots(db)
    query = db.query(models.DeliverySlot).filter(models.DeliverySlot.is_active == True)
    if target_date:
        query = query.filter(models.DeliverySlot.slot_date == target_date)
    slots = query.order_by(models.DeliverySlot.slot_date, models.DeliverySlot.id).all()
    
    result = []
    for s in slots:
        spots_left = max(0, s.max_capacity - s.booked_count)
        result.append({
            "id": s.id,
            "slot_date": s.slot_date,
            "time_window": s.time_window,
            "slot_label": s.slot_label,
            "max_capacity": s.max_capacity,
            "booked_count": s.booked_count,
            "is_active": s.is_active,
            "available_spots": spots_left,
            "is_full": spots_left <= 0
        })
    return result


# ================= ORDER & CHECKOUT OPERATIONS =================
def create_order(db: Session, order_in: schemas.OrderCreate):
    # 1. Verify Slot
    slot = db.query(models.DeliverySlot).filter(models.DeliverySlot.id == order_in.slot_id).first()
    if not slot:
        raise ValueError("Selected delivery slot is invalid.")
    if slot.booked_count >= slot.max_capacity:
        raise ValueError("Selected delivery slot is fully booked. Please choose another slot.")

    # 2. Verify and calculate items
    subtotal = 0.0
    order_items_data = []

    for item in order_in.items:
        prod = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not prod:
            raise ValueError(f"Product with ID {item.product_id} was not found.")
        if prod.stock_quantity < item.quantity:
            raise ValueError(
                f"Insufficient godown stock for '{prod.name}'. Requested: {item.quantity}, Available: {prod.stock_quantity}."
            )
        
        # Deduct Godown Stock
        prod.stock_quantity -= item.quantity
        if prod.stock_quantity == 0:
            prod.is_available = False

        item_total = round(prod.price * item.quantity, 2)
        subtotal += item_total
        order_items_data.append({
            "product_id": prod.id,
            "product_name": prod.name,
            "unit": prod.unit,
            "price": prod.price,
            "quantity": item.quantity,
            "total_price": item_total
        })

    # 3. Coupons & Discounts
    discount = 0.0
    if order_in.coupon_code:
        code = order_in.coupon_code.strip().upper()
        if code == "UCTNEW":
            discount = round(subtotal * 0.15, 2) # 15% off
        elif code == "FRESH50":
            discount = round(min(subtotal * 0.10, 50.0), 2) # 10% up to $50

    # 4. Delivery fee & Tax calculation
    discounted_subtotal = max(0.0, subtotal - discount)
    delivery_fee = 0.0 if discounted_subtotal >= MIN_ORDER_FREE_DELIVERY else STANDARD_DELIVERY_FEE
    tax_amount = round(discounted_subtotal * TAX_RATE, 2)
    total_amount = round(discounted_subtotal + delivery_fee + tax_amount, 2)

    # 5. Generate Order Number & Transaction ID
    order_num = f"UCT-GODOWN-{uuid.uuid4().hex[:7].upper()}"
    tx_id = f"TXN-{uuid.uuid4().hex[:10].upper()}" if order_in.payment_method != "COD" else None
    payment_status = "PAID" if order_in.payment_method != "COD" else "PENDING"

    # 6. Book slot spot
    slot.booked_count += 1

    # 7. Create Order Record
    db_order = models.Order(
        order_number=order_num,
        customer_name=order_in.customer_name,
        customer_email=order_in.customer_email,
        customer_phone=order_in.customer_phone,
        delivery_address=order_in.delivery_address,
        delivery_city=order_in.delivery_city,
        delivery_pincode=order_in.delivery_pincode,
        delivery_notes=order_in.delivery_notes,
        slot_id=slot.id,
        slot_date=slot.slot_date,
        slot_window=slot.time_window,
        subtotal=round(subtotal, 2),
        discount_amount=discount,
        delivery_fee=delivery_fee,
        tax_amount=tax_amount,
        total_amount=total_amount,
        payment_method=order_in.payment_method,
        payment_status=payment_status,
        transaction_id=tx_id,
        order_status="PLACED",
        driver_name="Ramesh Verma (Godown Logistics Hub 4)",
        driver_phone="+91 98112 34567",
        current_lat=GODOWN_LAT,
        current_lng=GODOWN_LNG,
        est_eta_minutes=35
    )
    db.add(db_order)
    db.flush()

    # 8. Create Order Items
    for item_data in order_items_data:
        db_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order

def get_order_by_number(db: Session, order_number: str):
    return db.query(models.Order).filter(models.Order.order_number == order_number).first()

def get_orders(db: Session, limit: int = 50):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).limit(limit).all()

def update_order_status(db: Session, order_id: int, status_in: schemas.OrderStatusUpdate):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None
    order.order_status = status_in.order_status
    if status_in.driver_name:
        order.driver_name = status_in.driver_name
    if status_in.driver_phone:
        order.driver_phone = status_in.driver_phone
    if status_in.est_eta_minutes is not None:
        order.est_eta_minutes = status_in.est_eta_minutes
    if status_in.order_status == "DELIVERED":
        order.payment_status = "PAID"
        order.est_eta_minutes = 0
    db.commit()
    db.refresh(order)
    return order


# ================= ADMIN ANALYTICS =================
def get_admin_stats(db: Session):
    total_orders = db.query(models.Order).count()
    revenue_sum = db.query(func.sum(models.Order.total_amount)).filter(models.Order.payment_status == "PAID").scalar() or 0.0
    pending_fulfillment = db.query(models.Order).filter(models.Order.order_status.in_(["PLACED", "PICKED_FROM_GODOWN", "PACKED"])).count()
    active_deliveries = db.query(models.Order).filter(models.Order.order_status == "OUT_FOR_DELIVERY").count()
    total_products = db.query(models.Product).count()
    low_stock_count = db.query(models.Product).filter(models.Product.stock_quantity <= models.Product.low_stock_threshold).count()
    
    # Slot utilization
    total_slot_capacity = db.query(func.sum(models.DeliverySlot.max_capacity)).scalar() or 1
    total_slot_booked = db.query(func.sum(models.DeliverySlot.booked_count)).scalar() or 0
    slot_utilization_percent = round((total_slot_booked / total_slot_capacity) * 100, 1)

    return {
        "total_orders": total_orders,
        "total_revenue": round(revenue_sum, 2),
        "pending_fulfillment": pending_fulfillment,
        "active_deliveries": active_deliveries,
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "slot_utilization_percent": slot_utilization_percent
    }
