from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db, SessionLocal
from app.config import APP_NAME, ORGANIZATION
from app.routers import products, slots, orders, admin
from app import crud

# Create all database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    db = SessionLocal()
    try:
        crud.ensure_default_slots(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=APP_NAME,
    description=f"Full Stack Internship Project developed for {ORGANIZATION}. Large-scale departmental grocery store with godown inventory, delivery slot selection, payment gateway, and live driver tracking.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files and Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API Routers
app.include_router(products.router)
app.include_router(slots.router)
app.include_router(orders.router)
app.include_router(admin.router)

# Frontend HTML Page Routes
@app.get("/", summary="Customer Storefront")
def index_view(request: Request, db: Session = Depends(get_db)):
    categories = crud.get_categories(db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": APP_NAME,
            "company": ORGANIZATION,
            "categories": categories
        }
    )

@app.get("/track/{order_number}", summary="Order Tracking & Driver Geolocation")
def tracking_view(order_number: str, request: Request, db: Session = Depends(get_db)):
    order = crud.get_order_by_number(db, order_number)
    return templates.TemplateResponse(
        request=request,
        name="tracking.html",
        context={
            "app_name": APP_NAME,
            "company": ORGANIZATION,
            "order_number": order_number,
            "order_exists": order is not None
        }
    )

@app.get("/admin", summary="Godown Manager & Admin Portal")
def admin_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "app_name": APP_NAME,
            "company": ORGANIZATION
        }
    )
