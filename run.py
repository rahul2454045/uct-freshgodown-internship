import os
import uvicorn
from seed_data import seed
from app.database import engine, Base
from app import models

def main():
    print("=" * 60)
    print(" FRESHGODOWN - DEPARTMENTAL GROCERY STORE PLATFORM")
    print(" Full Stack Internship Capstone Project by UCT")
    print("=" * 60)

    # Ensure database is initialized
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if database is empty
    from app.database import SessionLocal
    db = SessionLocal()
    has_products = db.query(models.Product).first() is not None
    db.close()

    if not has_products:
        print("[*] Empty database detected. Populating with realistic departmental catalog...")
        seed()

    print("\n[+] System ready! Access the application via:")
    print("    - Customer Storefront:   http://127.0.0.1:8000/")
    print("    - Live Driver GPS:       http://127.0.0.1:8000/track/UCT-DEMO-001")
    print("    - Godown Manager Portal: http://127.0.0.1:8000/admin")
    print("    - Interactive API Docs:  http://127.0.0.1:8000/docs\n")

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
