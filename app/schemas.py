from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = "shopping-bag"
    display_order: int = 0

class CategoryOut(CategoryBase):
    id: int
    product_count: Optional[int] = 0
    model_config = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    name: str
    slug: str
    category_id: int
    description: Optional[str] = None
    unit: str
    price: float
    mrp: float
    stock_quantity: int
    low_stock_threshold: int = 15
    is_available: bool = True
    image_url: Optional[str] = None
    badge: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    is_available: Optional[bool] = None
    badge: Optional[str] = None

class ProductOut(ProductBase):
    id: int
    rating: float
    review_count: int
    created_at: datetime
    category_name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# Delivery Slot Schemas
class SlotBase(BaseModel):
    slot_date: str
    time_window: str
    slot_label: str
    max_capacity: int = 15

class SlotOut(SlotBase):
    id: int
    booked_count: int
    is_active: bool
    available_spots: int
    is_full: bool
    model_config = ConfigDict(from_attributes=True)


# Cart & Checkout Schemas
class CartItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than zero")

class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_address: str
    delivery_city: str = "Central City"
    delivery_pincode: str
    delivery_notes: Optional[str] = None
    
    slot_id: int
    coupon_code: Optional[str] = None
    payment_method: str = "CARD" # CARD, UPI, NETBANKING, COD
    
    items: List[CartItemInput]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit: str
    price: float
    quantity: int
    total_price: float
    model_config = ConfigDict(from_attributes=True)

class OrderOut(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_address: str
    delivery_city: str
    delivery_pincode: str
    delivery_notes: Optional[str]
    slot_date: str
    slot_window: str
    subtotal: float
    discount_amount: float
    delivery_fee: float
    tax_amount: float
    total_amount: float
    payment_method: str
    payment_status: str
    transaction_id: Optional[str]
    order_status: str
    driver_name: Optional[str]
    driver_phone: Optional[str]
    current_lat: Optional[float]
    current_lng: Optional[float]
    est_eta_minutes: Optional[int]
    created_at: datetime
    items: List[OrderItemOut]
    model_config = ConfigDict(from_attributes=True)

class OrderStatusUpdate(BaseModel):
    order_status: str
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    est_eta_minutes: Optional[int] = None

# Review Schemas
class ReviewCreate(BaseModel):
    product_id: int
    reviewer_name: str
    rating: int = Field(ge=1, le=5)
    comment: str

class ReviewOut(BaseModel):
    id: int
    product_id: int
    reviewer_name: str
    rating: int
    comment: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Admin KPI & Analytics Schema
class AdminStatsOut(BaseModel):
    total_orders: int
    total_revenue: float
    pending_fulfillment: int
    active_deliveries: int
    total_products: int
    low_stock_count: int
    slot_utilization_percent: float
