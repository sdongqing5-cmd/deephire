"""Database initialization script

Run this to initialize the database with tables and seed data.

Usage:
    python -m app.db.init_db
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.init_db import main

if __name__ == "__main__":
    main()
