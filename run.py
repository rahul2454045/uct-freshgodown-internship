import sys
import socket
import uvicorn
from seed_data import seed
from app.database import engine, Base
from app import models

def find_available_port(default_port=8000, fallbacks=[8080, 5000, 8888, 3000]):
    ports = [default_port] + fallbacks
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return default_port

def main():
    print("=" * 65)
    print(" FRESHGODOWN - ONLINE DEPARTMENTAL STORE & GROCERY DELIVERY")
    print(" Full Stack Internship Capstone Project by UCT")
    print("=" * 65)

    # Initialize database
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if database is empty
    from app.database import SessionLocal
    db = SessionLocal()
    has_products = db.query(models.Product).first() is not None
    db.close()

    if not has_products:
        print("[*] Empty database detected. Populating with realistic departmental catalog...")
        seed()

    # Determine open port
    port = find_available_port(8000)

    print(f"\n[+] Server is starting successfully on Port {port}!")
    print(f"    - Customer Storefront:   http://127.0.0.1:{port}/")
    print(f"    - Live Driver GPS:       http://127.0.0.1:{port}/track/UCT-DEMO-001")
    print(f"    - Godown Manager Portal: http://127.0.0.1:{port}/admin")
    print(f"    - Interactive API Docs:  http://127.0.0.1:{port}/docs\n")
    print("Press CTRL+C to stop the server.\n")

    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)

if __name__ == "__main__":
    main()
