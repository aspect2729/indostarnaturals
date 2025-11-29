#!/usr/bin/env python3
"""
Run database migrations on production
Usage: python run_migrations.py
"""
import subprocess
import sys

def run_migrations():
    """Run Alembic migrations"""
    print("🔄 Running database migrations...")
    
    try:
        # Run alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Migrations completed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Migration failed!")
        print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
