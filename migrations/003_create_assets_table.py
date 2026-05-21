"""
Database Migration 003: Create Assets Table
Creates the assets table for asset management module
"""

import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db


def up():
    """Apply migration"""
    db = get_db()
    
    # Check if table exists
    result = db.fetch_one("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='assets'
    """)
    
    if result:
        print("[SKIP] assets table already exists")
        return
    
    print("[CREATING] assets table...")
    
    db.execute("""
        CREATE TABLE assets (
            asset_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            purchase_date DATE NOT NULL,
            purchase_cost REAL NOT NULL,
            salvage_value REAL DEFAULT 0,
            useful_life_years INTEGER,
            depreciation_method TEXT DEFAULT 'Straight-Line',
            book_value REAL,
            accumulated_depreciation REAL DEFAULT 0,
            location TEXT,
            serial_number TEXT,
            status TEXT DEFAULT 'Active',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            disposed_date DATE,
            disposed_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (disposed_by) REFERENCES users(id)
        )
    """)
    
    db.execute("""
        CREATE TABLE asset_depreciation_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id TEXT NOT NULL,
            depreciation_date DATE NOT NULL,
            depreciation_amount REAL NOT NULL,
            book_value_after REAL NOT NULL,
            recorded_by INTEGER,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
            FOREIGN KEY (recorded_by) REFERENCES users(id)
        )
    """)
    
    print("[OK] assets table created")
    print("[OK] asset_depreciation_log table created")


def down():
    """Rollback migration"""
    db = get_db()
    
    print("[ROLLBACK] Dropping asset_depreciation_log...")
    db.execute("DROP TABLE IF EXISTS asset_depreciation_log")
    
    print("[ROLLBACK] Dropping assets...")
    db.execute("DROP TABLE IF EXISTS assets")
    
    print("[OK] Rollback complete")


if __name__ == "__main__":
    print("=" * 60)
    print("Migration 003: Create Assets Table")
    print("=" * 60)
    
    try:
        up()
        print("\n[SUCCESS] Migration completed")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
