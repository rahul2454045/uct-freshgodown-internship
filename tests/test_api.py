import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app import models

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    from seed_data import seed
    seed()
    yield

def test_frontend_views():
    r_home = client.get("/")
    assert r_home.status_code == 200
    assert "FreshGodown" in r_home.text

    r_admin = client.get("/admin")
    assert r_admin.status_code == 200
    assert "Godown Operations Portal" in r_admin.text

    r_track = client.get("/track/UCT-DEMO-001")
    assert r_track.status_code == 200
    assert "Live Delivery Tracking" in r_track.text

def test_list_categories():
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 6
    names = [c["name"] for c in data]
    assert "Fresh Fruits & Vegetables" in names
    assert "Godown Staples & Grains" in names

def test_list_products_and_search():
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    response_search = client.get("/api/products?search=Apples")
    assert response_search.status_code == 200
    search_data = response_search.json()
    assert len(search_data) >= 1
    assert "Apple" in search_data[0]["name"]

def test_delivery_slots_availability():
    response = client.get("/api/slots")
    assert response.status_code == 200
    slots = response.json()
    assert len(slots) >= 4
    for slot in slots:
        assert "time_window" in slot
        assert "available_spots" in slot
        assert slot["available_spots"] >= 0

def test_place_order_and_stock_deduction():
    prod_res = client.get("/api/products?search=Bananas")
    product = prod_res.json()[0]
    initial_stock = product["stock_quantity"]
    prod_id = product["id"]

    slots_res = client.get("/api/slots")
    slot = slots_res.json()[0]
    slot_id = slot["id"]

    order_payload = {
        "customer_name": "Test Customer",
        "customer_email": "test@uct.edu",
        "customer_phone": "+91 99999 88888",
        "delivery_address": "Flat 101, Test Residency",
        "delivery_city": "Test Metro",
        "delivery_pincode": "110022",
        "delivery_notes": "Call upon arrival",
        "slot_id": slot_id,
        "coupon_code": "UCTNEW",
        "payment_method": "UPI",
        "items": [
            {"product_id": prod_id, "quantity": 3}
        ]
    }

    response = client.post("/api/orders", json=order_payload)
    assert response.status_code == 201
    order = response.json()
    assert order["order_number"].startswith("UCT-GODOWN-")
    assert order["customer_name"] == "Test Customer"
    assert order["payment_status"] == "PAID"
    assert order["discount_amount"] > 0

    prod_after = client.get(f"/api/products/{prod_id}").json()
    assert prod_after["stock_quantity"] == initial_stock - 3

def test_insufficient_stock_rejection():
    prod_res = client.get("/api/products?search=Bananas")
    product = prod_res.json()[0]
    slots_res = client.get("/api/slots")
    slot = slots_res.json()[0]

    order_payload = {
        "customer_name": "Greedy Buyer",
        "customer_email": "greedy@example.com",
        "customer_phone": "+91 99999 11111",
        "delivery_address": "Somewhere",
        "delivery_pincode": "110001",
        "slot_id": slot["id"],
        "items": [
            {"product_id": product["id"], "quantity": 999999}
        ]
    }
    response = client.post("/api/orders", json=order_payload)
    assert response.status_code == 400
    assert "Insufficient godown stock" in response.json()["detail"]

def test_order_tracking_and_driver_simulation():
    tracking_res = client.get("/api/orders/UCT-DEMO-001/tracking")
    assert tracking_res.status_code == 200
    track = tracking_res.json()
    assert track["order_number"] == "UCT-DEMO-001"
    assert "driver" in track
    assert "lat" in track["driver"]
    assert "lng" in track["driver"]
    assert "milestones" in track
    assert len(track["milestones"]) == 5

def test_admin_portal_kpis_and_restock():
    stats_res = client.get("/api/admin/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_orders" in stats
    assert stats["total_orders"] >= 1
    assert "total_revenue" in stats

    prods = client.get("/api/products").json()
    p_id = prods[0]["id"]
    current_qty = prods[0]["stock_quantity"]

    restock_res = client.post(f"/api/admin/inventory/{p_id}/restock?add_quantity=50")
    assert restock_res.status_code == 200
    assert restock_res.json()["new_stock"] == current_qty + 50
