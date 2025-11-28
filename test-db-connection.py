"""Test database connection"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
            
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("\nPossible issues:")
    print("1. PostgreSQL is not running")
    print("2. Database 'indostar_naturals' doesn't exist")
    print("3. Wrong username/password in backend/.env")
    print("4. Wrong host/port")
