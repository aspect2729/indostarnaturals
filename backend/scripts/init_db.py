"""Initialize database with migrations"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from alembic.config import Config
from alembic import command


def init_db():
    """Run all database migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database initialized successfully!")
    print("\nDefault owner credentials:")
    print("Phone: +919999999999")
    print("Password: admin123")
    print("\n⚠️  IMPORTANT: Change these credentials after first login!")


if __name__ == "__main__":
    init_db()
