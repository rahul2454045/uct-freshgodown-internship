import os

APP_NAME = "FreshGodown - Online Departmental Store & Grocery Delivery"
ORGANIZATION = "UCT (Universal Creative Technologies)"
PROJECT_TRACK = "Track 5: Large-Scale Grocery Delivery Application"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./freshgodown.db")
SECRET_KEY = os.getenv("SECRET_KEY", "uct-internship-super-secret-key-2026")
MIN_ORDER_FREE_DELIVERY = 35.00
STANDARD_DELIVERY_FEE = 4.50
EXPRESS_SURCHARGE = 2.50
TAX_RATE = 0.05  # 5% tax

# Godown central coordinates for simulated driver tracking (e.g., Metro Hub)
GODOWN_LAT = 28.6139
GODOWN_LNG = 77.2090
