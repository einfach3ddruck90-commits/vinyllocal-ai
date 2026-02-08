"""
Einmal-Skript: Erstellt cloud_demo_assets/ mit vinyl_demo.db (Schema + Demo-Kunden)
und leerem vinyl_images/. Für Cloud-Demo-Deployment.
Ausführung vom Projektroot: python scripts/seed_cloud_demo_db.py
"""
import os
import sys

# Projektroot = übergeordnetes Verzeichnis von scripts/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

ASSETS_DIR = os.path.join(PROJECT_ROOT, "cloud_demo_assets")
DEMO_DB_PATH = os.path.join(ASSETS_DIR, "vinyl_demo.db")
VINYL_IMAGES_DIR = os.path.join(ASSETS_DIR, "vinyl_images")


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(VINYL_IMAGES_DIR, exist_ok=True)

    from database.local_db import Database
    db = Database(db_path=DEMO_DB_PATH)

    # Vorgegebene Demo-Kunden
    demo_customers = [
        {
            "name": "Demo Kunde 1",
            "street": "Musterstraße",
            "house_number": "1",
            "postal_code": "10115",
            "city": "Berlin",
            "country": "Deutschland",
            "email": "demo1@example.com",
            "phone": "+49 30 123456",
        },
        {
            "name": "Demo Kunde 2",
            "street": "Beispielweg",
            "house_number": "42",
            "postal_code": "80331",
            "city": "München",
            "country": "Deutschland",
            "email": "demo2@example.com",
            "phone": "+49 89 654321",
        },
        {
            "name": "Demo Kunde 3",
            "street": "Testallee",
            "house_number": "7",
            "postal_code": "20095",
            "city": "Hamburg",
            "country": "Deutschland",
            "email": "demo3@example.com",
            "phone": "",
        },
    ]

    for data in demo_customers:
        db.add_customer(data)

    # Company Settings: Platzhalter für Shopify Demo-Store (Option A).
    # Vor Deploy: shopify_store_url und shopify_access_token mit Demo-Shop eintragen.
    settings = db.get_company_settings() or {}
    if not settings.get("shopify_store_url"):
        db.update_company_settings({
            "shopify_enabled": 0,
            "shopify_store_url": "",
            "shopify_access_token": "",
        })

    print("cloud_demo_assets erstellt:")
    print("  -", DEMO_DB_PATH)
    print("  -", VINYL_IMAGES_DIR, "(leer)")
    print("Demo-Kunden:", len(demo_customers))


if __name__ == "__main__":
    main()
