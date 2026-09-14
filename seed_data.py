from datetime import datetime, date, timedelta
from app.database import SessionLocal, engine, Base
from app import models

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("Checking existing data...")
    if db.query(models.Category).first():
        print("Database already contains data. Cleaning and re-seeding for clean demo...")
        db.query(models.OrderItem).delete()
        db.query(models.Order).delete()
        db.query(models.Review).delete()
        db.query(models.Product).delete()
        db.query(models.DeliverySlot).delete()
        db.query(models.Category).delete()
        db.commit()

    print("Seeding departmental categories...")
    categories_data = [
        {"name": "Fresh Fruits & Vegetables", "slug": "produce", "description": "Farm-fresh organic fruits and crisp vegetables directly from regional growers to our godown.", "icon": "salad", "display_order": 1},
        {"name": "Dairy, Bread & Eggs", "slug": "dairy-bakery", "description": "Chilled milk, artisanal breads, organic eggs, and artisanal cheeses.", "icon": "milk", "display_order": 2},
        {"name": "Godown Staples & Grains", "slug": "staples", "description": "Bulk godown storage of premium Basmati rice, unpolished pulses, flour, and cold-pressed oils.", "icon": "wheat", "display_order": 3},
        {"name": "Beverages & Cold Drinks", "slug": "beverages", "description": "100% pure juices, artisan roasted coffee beans, botanical herbal teas, and mineral waters.", "icon": "coffee", "display_order": 4},
        {"name": "Snacks & Packaged Food", "slug": "snacks", "description": "Gourmet dark chocolates, roasted nuts, whole grain granola, and Italian pasta.", "icon": "cookie", "display_order": 5},
        {"name": "Household & Cleaning", "slug": "household", "description": "Eco-friendly detergents, biodegradable surface cleaners, and kitchen paper essentials.", "icon": "sparkles", "display_order": 6},
    ]

    cat_map = {}
    for c_data in categories_data:
        cat = models.Category(**c_data)
        db.add(cat)
        db.flush()
        cat_map[c_data["slug"]] = cat.id

    print("Seeding godown grocery products...")
    products_data = [
        # Fresh Fruits & Vegetables
        {
            "name": "Fresh Organic Red Gala Apples",
            "slug": "organic-red-apples",
            "category_id": cat_map["produce"],
            "description": "Crisp, sweet, and hand-selected Washington Gala apples. Freshly arriving in climate-controlled godown crates daily.",
            "unit": "1 kg (approx 4-5 pcs)",
            "price": 3.99,
            "mrp": 4.99,
            "stock_quantity": 180,
            "low_stock_threshold": 25,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&auto=format&fit=crop&q=80",
            "badge": "Fresh Harvest",
            "rating": 4.9,
            "review_count": 86
        },
        {
            "name": "Farm Fresh Robusta Bananas",
            "slug": "fresh-bananas",
            "category_id": cat_map["produce"],
            "description": "Naturally ripened golden bananas rich in potassium and quick carbohydrates for sustained energy.",
            "unit": "1 dozen (12 pcs)",
            "price": 1.89,
            "mrp": 2.49,
            "stock_quantity": 240,
            "low_stock_threshold": 30,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600&auto=format&fit=crop&q=80",
            "badge": "Godown Saver",
            "rating": 4.8,
            "review_count": 112
        },
        {
            "name": "Hydroponic Crisp Baby Spinach",
            "slug": "hydroponic-spinach",
            "category_id": cat_map["produce"],
            "description": "Pre-washed, pesticide-free baby spinach leaves packed in protective oxygenated seal bags.",
            "unit": "250 g pack",
            "price": 2.49,
            "mrp": 3.20,
            "stock_quantity": 90,
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600&auto=format&fit=crop&q=80",
            "badge": "Organic",
            "rating": 4.7,
            "review_count": 45
        },
        {
            "name": "Vine-Ripened Cherry Tomatoes",
            "slug": "cherry-tomatoes",
            "category_id": cat_map["produce"],
            "description": "Sweet, juicy ruby-red cherry tomatoes bursting with fresh summer flavour. Ideal for salads and roasting.",
            "unit": "500 g punnet",
            "price": 2.99,
            "mrp": 3.75,
            "stock_quantity": 12, # Low stock demo!
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&auto=format&fit=crop&q=80",
            "badge": "Low Stock Alert",
            "rating": 4.8,
            "review_count": 67
        },
        {
            "name": "Golden Hass Avocados",
            "slug": "hass-avocados",
            "category_id": cat_map["produce"],
            "description": "Creamy, ready-to-eat Hass avocados with rich healthy fats. Sourced from certified orchards.",
            "unit": "Pack of 2",
            "price": 3.49,
            "mrp": 4.50,
            "stock_quantity": 65,
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=600&auto=format&fit=crop&q=80",
            "badge": "Bestseller",
            "rating": 4.9,
            "review_count": 94
        },

        # Dairy, Bread & Eggs
        {
            "name": "Farmstead A2 Organic Whole Milk",
            "slug": "a2-organic-whole-milk",
            "category_id": cat_map["dairy-bakery"],
            "description": "Single-origin pasteurized whole milk from grass-fed cows. Preserved in chilled godown cold storage at 3°C.",
            "unit": "1 Liter Glass Bottle",
            "price": 2.89,
            "mrp": 3.50,
            "stock_quantity": 140,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&auto=format&fit=crop&q=80",
            "badge": "Chilled Cold-Chain",
            "rating": 4.9,
            "review_count": 130
        },
        {
            "name": "Artisanal Sourdough Bread Loaf",
            "slug": "artisanal-sourdough-bread",
            "category_id": cat_map["dairy-bakery"],
            "description": "Slow-fermented 36-hour sourdough with a crispy caramel crust and airy, chewy crumb structure.",
            "unit": "500 g loaf",
            "price": 3.75,
            "mrp": 4.50,
            "stock_quantity": 40,
            "low_stock_threshold": 10,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?w=600&auto=format&fit=crop&q=80",
            "badge": "Fresh Baked Daily",
            "rating": 4.8,
            "review_count": 52
        },
        {
            "name": "Free-Range Golden Yolk Brown Eggs",
            "slug": "free-range-brown-eggs",
            "category_id": cat_map["dairy-bakery"],
            "description": "Grade-A pasture-raised brown eggs with rich deep-golden yolks. Packed with high protein & Omega-3.",
            "unit": "12 pcs carton",
            "price": 4.29,
            "mrp": 5.00,
            "stock_quantity": 110,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1516448620398-c5f44bf9f441?w=600&auto=format&fit=crop&q=80",
            "badge": "Pasture Raised",
            "rating": 4.9,
            "review_count": 180
        },
        {
            "name": "Salted European Butter Block",
            "slug": "salted-european-butter",
            "category_id": cat_map["dairy-bakery"],
            "description": "82% butterfat cultured cream butter with fine sea salt crystals. Perfect for baking and flaky pastries.",
            "unit": "250 g block",
            "price": 3.19,
            "mrp": 3.99,
            "stock_quantity": 85,
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600&auto=format&fit=crop&q=80",
            "badge": "Imported",
            "rating": 4.7,
            "review_count": 39
        },
        {
            "name": "Greek Strained Probiotic Yogurt",
            "slug": "greek-strained-yogurt",
            "category_id": cat_map["dairy-bakery"],
            "description": "Thick, velvety unsweetened authentic Greek yogurt with active live gut-friendly cultures.",
            "unit": "400 g tub",
            "price": 2.99,
            "mrp": 3.60,
            "stock_quantity": 70,
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600&auto=format&fit=crop&q=80",
            "badge": "Probiotic",
            "rating": 4.8,
            "review_count": 64
        },

        # Godown Staples & Grains
        {
            "name": "Royal Aged Extra Long Basmati Rice",
            "slug": "royal-aged-basmati-rice",
            "category_id": cat_map["staples"],
            "description": "2-year Himalayan aged long grain basmati rice. Delivers unmatched aroma and slender elongation when cooked.",
            "unit": "5 kg Godown Sack",
            "price": 14.99,
            "mrp": 19.99,
            "stock_quantity": 150,
            "low_stock_threshold": 25,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
            "badge": "Godown Bulk Saver",
            "rating": 4.9,
            "review_count": 210
        },
        {
            "name": "Stone-Ground Whole Wheat Atta",
            "slug": "stone-ground-wheat-atta",
            "category_id": cat_map["staples"],
            "description": "100% chakki-milled whole wheat flour with dietary fiber and germ intact for soft, fluffy rotis.",
            "unit": "10 kg Sack",
            "price": 11.49,
            "mrp": 14.00,
            "stock_quantity": 200,
            "low_stock_threshold": 30,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80",
            "badge": "Essential Staple",
            "rating": 4.8,
            "review_count": 145
        },
        {
            "name": "Cold Pressed Extra Virgin Olive Oil",
            "slug": "extra-virgin-olive-oil",
            "category_id": cat_map["staples"],
            "description": "First cold extraction Spanish Arbequina olive oil with polyphenol antioxidants and peppery finish.",
            "unit": "1 Liter Tin",
            "price": 12.99,
            "mrp": 16.50,
            "stock_quantity": 9, # Low stock demo!
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
            "badge": "Low Stock Alert",
            "rating": 4.9,
            "review_count": 78
        },
        {
            "name": "Unpolished Organic Toor Dal",
            "slug": "organic-toor-dal",
            "category_id": cat_map["staples"],
            "description": "Pesticide-free yellow pigeon peas without water polish or synthetic oils. Cooks easily into savory dal.",
            "unit": "1 kg pack",
            "price": 3.49,
            "mrp": 4.25,
            "stock_quantity": 175,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?w=600&auto=format&fit=crop&q=80",
            "badge": "Unpolished",
            "rating": 4.8,
            "review_count": 92
        },

        # Beverages & Cold Drinks
        {
            "name": "Valencia Pure Squeezed Orange Juice",
            "slug": "pure-orange-juice",
            "category_id": cat_map["beverages"],
            "description": "100% freshly pressed Valencia oranges with gentle pulp. Zero added sugar or preservatives.",
            "unit": "1 Liter Carafe",
            "price": 3.99,
            "mrp": 4.99,
            "stock_quantity": 120,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=600&auto=format&fit=crop&q=80",
            "badge": "Zero Added Sugar",
            "rating": 4.9,
            "review_count": 105
        },
        {
            "name": "Artisan Single-Origin Arabica Coffee",
            "slug": "arabica-coffee-beans",
            "category_id": cat_map["beverages"],
            "description": "Medium-dark roasted 100% Arabica beans with notes of hazelnut, dark cocoa, and caramel sweetness.",
            "unit": "500 g pouch",
            "price": 8.99,
            "mrp": 11.50,
            "stock_quantity": 75,
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=600&auto=format&fit=crop&q=80",
            "badge": "Specialty Roast",
            "rating": 4.9,
            "review_count": 88
        },
        {
            "name": "Japanese Organic Matcha Green Tea",
            "slug": "japanese-matcha-tea",
            "category_id": cat_map["beverages"],
            "description": "Ceremonial grade stone-ground Uji green tea leaf powder loaded with L-theanine and clean energy.",
            "unit": "100 g tin",
            "price": 9.49,
            "mrp": 12.00,
            "stock_quantity": 50,
            "low_stock_threshold": 10,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80",
            "badge": "Antioxidant Rich",
            "rating": 4.8,
            "review_count": 42
        },

        # Snacks & Packaged Food
        {
            "name": "California Whole Roasted Almonds",
            "slug": "whole-roasted-almonds",
            "category_id": cat_map["snacks"],
            "description": "Lightly salted jumbo California almonds slow roasted without oil. Nutritious midday snack.",
            "unit": "500 g resealable pouch",
            "price": 7.49,
            "mrp": 9.99,
            "stock_quantity": 95,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1508061252445-5350f3ab0a55?w=600&auto=format&fit=crop&q=80",
            "badge": "Heart Healthy",
            "rating": 4.9,
            "review_count": 133
        },
        {
            "name": "Belgian 72% Dark Cocoa Chocolate",
            "slug": "belgian-dark-chocolate",
            "category_id": cat_map["snacks"],
            "description": "Smooth, bittersweet single-estate dark chocolate bar crafted by master Belgian chocolatiers.",
            "unit": "100 g bar",
            "price": 2.79,
            "mrp": 3.50,
            "stock_quantity": 110,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1549007994-cb92caebd54b?w=600&auto=format&fit=crop&q=80",
            "badge": "Gourmet",
            "rating": 4.8,
            "review_count": 76
        },
        {
            "name": "Bronze-Cut Italian Penne Rigate",
            "slug": "bronze-cut-penne",
            "category_id": cat_map["snacks"],
            "description": "100% durum wheat semolina pasta extruded through bronze dies for authentic rough sauce-clinging texture.",
            "unit": "500 g box",
            "price": 2.19,
            "mrp": 2.89,
            "stock_quantity": 130,
            "low_stock_threshold": 25,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1621996346565-e3d5d6281691?w=600&auto=format&fit=crop&q=80",
            "badge": "Product of Italy",
            "rating": 4.7,
            "review_count": 59
        },

        # Household & Cleaning
        {
            "name": "Botanical Plant-Powered Dish Soap",
            "slug": "botanical-dish-soap",
            "category_id": cat_map["household"],
            "description": "Gentle on hands, ruthless on grease. Infused with natural lemon verbena and aloe vera extracts.",
            "unit": "750 ml bottle",
            "price": 3.49,
            "mrp": 4.25,
            "stock_quantity": 140,
            "low_stock_threshold": 20,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=600&auto=format&fit=crop&q=80",
            "badge": "Eco Friendly",
            "rating": 4.8,
            "review_count": 81
        },
        {
            "name": "Concentrated Eco Laundry Detergent",
            "slug": "eco-laundry-detergent",
            "category_id": cat_map["household"],
            "description": "Hypoallergenic enzyme-based formula safe for sensitive skin and infant clothes. 64 wash loads.",
            "unit": "2 Liter Jug",
            "price": 9.99,
            "mrp": 12.99,
            "stock_quantity": 60,
            "low_stock_threshold": 15,
            "is_available": True,
            "image_url": "https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=600&auto=format&fit=crop&q=80",
            "badge": "Hypoallergenic",
            "rating": 4.9,
            "review_count": 97
        }
    ]

    for p_data in products_data:
        prod = models.Product(**p_data)
        db.add(prod)

    db.commit()

    print("Generating scheduled delivery slots...")
    today = date.today()
    standard_windows = [
        ("06:00 AM - 08:00 AM", "Early Morning Fresh Slot"),
        ("09:00 AM - 11:00 AM", "Morning Rush Delivery"),
        ("02:00 PM - 04:00 PM", "Afternoon Express"),
        ("07:00 PM - 09:00 PM", "Evening Prime Delivery")
    ]
    created_slots = []
    for offset in range(3):
        day = today + timedelta(days=offset)
        day_str = day.isoformat()
        for window, label in standard_windows:
            slot = models.DeliverySlot(
                slot_date=day_str,
                time_window=window,
                slot_label=label,
                max_capacity=15,
                booked_count=3 if offset == 0 else 1,
                is_active=True
            )
            db.add(slot)
            db.flush()
            created_slots.append(slot)
    db.commit()

    print("Seeding demo order for live driver tracking demonstration...")
    sample_order = models.Order(
        order_number="UCT-DEMO-001",
        customer_name="Priya Sharma",
        customer_email="priya.sharma@uct-demo.com",
        customer_phone="+91 98765 12345",
        delivery_address="Flat 402, Lotus Orchid Heights, Sector 18",
        delivery_city="Central City",
        delivery_pincode="110001",
        delivery_notes="Please ring doorbell and leave on porch table if unattended.",
        slot_id=created_slots[0].id,
        slot_date=created_slots[0].slot_date,
        slot_window=created_slots[0].time_window,
        subtotal=42.85,
        discount_amount=6.43,
        delivery_fee=0.0,
        tax_amount=1.82,
        total_amount=38.24,
        payment_method="UPI",
        payment_status="PAID",
        transaction_id="TXN-UPI-9842109X",
        order_status="OUT_FOR_DELIVERY",
        driver_name="Ramesh Verma (Godown Logistics Hub 4)",
        driver_phone="+91 98112 34567",
        current_lat=28.6250,
        current_lng=77.2150,
        est_eta_minutes=18
    )
    db.add(sample_order)
    db.flush()

    # Add items to sample order
    first_prod = db.query(models.Product).first()
    second_prod = db.query(models.Product).filter(models.Product.id != first_prod.id).first()
    
    db.add(models.OrderItem(
        order_id=sample_order.id,
        product_id=first_prod.id,
        product_name=first_prod.name,
        unit=first_prod.unit,
        price=first_prod.price,
        quantity=2,
        total_price=round(first_prod.price * 2, 2)
    ))
    db.add(models.OrderItem(
        order_id=sample_order.id,
        product_id=second_prod.id,
        product_name=second_prod.name,
        unit=second_prod.unit,
        price=second_prod.price,
        quantity=3,
        total_price=round(second_prod.price * 3, 2)
    ))

    db.commit()
    db.close()
    print("Database seeding completed successfully! Ready for UCT Demonstration.")

if __name__ == "__main__":
    seed()
