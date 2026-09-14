from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    icon = Column(String(50), default="shopping-bag")
    display_order = Column(Integer, default=0)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=False, default="1 unit")
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=100, nullable=False)
    low_stock_threshold = Column(Integer, default=15)
    is_available = Column(Boolean, default=True)
    image_url = Column(String(500), nullable=True)
    badge = Column(String(50), nullable=True)
    rating = Column(Float, default=4.8)
    review_count = Column(Integer, default=24)
    created_at = Column(DateTime, default=utcnow)

    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")


class DeliverySlot(Base):
    __tablename__ = "delivery_slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_date = Column(String(20), nullable=False, index=True)
    time_window = Column(String(100), nullable=False)
    slot_label = Column(String(50), nullable=False)
    max_capacity = Column(Integer, default=15)
    booked_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="slot")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer Info
    customer_name = Column(String(120), nullable=False)
    customer_email = Column(String(120), nullable=False)
    customer_phone = Column(String(30), nullable=False)
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String(100), default="Central City")
    delivery_pincode = Column(String(20), nullable=False)
    delivery_notes = Column(String(255), nullable=True)

    # Slot Info
    slot_id = Column(Integer, ForeignKey("delivery_slots.id"), nullable=True)
    slot_date = Column(String(20), nullable=False)
    slot_window = Column(String(100), nullable=False)

    # Financials
    subtotal = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)

    # Payment
    payment_method = Column(String(30), nullable=False)
    payment_status = Column(String(30), default="PAID")
    transaction_id = Column(String(100), nullable=True)

    # Order Lifecycle
    order_status = Column(String(40), default="PLACED", index=True)
    
    # Delivery Driver details
    driver_name = Column(String(100), default="Rajesh Kumar")
    driver_phone = Column(String(30), default="+91 98765 43210")
    current_lat = Column(Float, default=28.6139)
    current_lng = Column(Float, default=77.2090)
    est_eta_minutes = Column(Integer, default=45)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    slot = relationship("DeliverySlot", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    unit = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    reviewer_name = Column(String(100), nullable=False)
    rating = Column(Integer, default=5)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    product = relationship("Product", back_populates="reviews")
