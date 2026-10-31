"""
Database Initialization & Seeding Script for Neon PostgreSQL
Usage: python seed_db.py
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import db

def main():
    print("Connecting to Neon PostgreSQL Database...")
    success, info = db.test_connection()
    if not success:
        print(f"❌ Connection failed: {info}")
        sys.exit(1)
    
    print(f"✅ Connection successful!\n{info}")
    print("\nInitializing database schema and seeding data...")
    try:
        db.init_db(seed_if_empty=True)
        # Verify count
        df = db.fetch_data()
        print(f"🎉 Verification successful: {len(df)} records are available in table '{db.TABLE_NAME}'!")
        print("\nFirst 3 rows in database:")
        print(df.head(3)[["Order_ID", "Date", "Customer_Name", "Product_Name", "Revenue"]])
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
