"""
Database Migration 002: Fix Expenses Table
Adds missing 'date' column to expenses table
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
    
    # Check if expenses table exists
    result = db.fetch_one("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='expenses'
    """)
    
    if not result:
        print("[ERROR] expenses table does not exist")
        return
    
    # Check if 'date' column exists
    # Get table info using raw SQL
    result = db.fetch_all("PRAGMA table_info(expenses)")
    columns = [row['name'] for row in result]
    
    if 'date' in columns:
        print("[SKIP] 'date' column already exists in expenses table")
        return
    
    print("[ADDING] 'date' column to expenses table...")
    
    # Add the column with NULL default (SQLite doesn't allow function defaults in ALTER)
    db.execute("""
        ALTER TABLE expenses 
        ADD COLUMN date DATE
    """)
    
    # Update existing rows to set date to today if NULL
    print("[UPDATING] Setting default dates for existing records...")
    db.execute("""
        UPDATE expenses 
        SET date = date('now')
        WHERE date IS NULL
    """)
    
    # If expense_date column exists, use it instead
    if 'expense_date' in columns:
        print("[MIGRATING] Copying expense_date to date column...")
        db.execute("""
            UPDATE expenses 
            SET date = expense_date 
            WHERE expense_date IS NOT NULL
        """)
    
    print("[OK] 'date' column added to expenses table")


def down():
    """Rollback migration"""
    print("[ROLLBACK] Cannot remove column in SQLite - manual intervention required")
    print("[INFO] To rollback, you would need to:")
    print("  1. Create new table without 'date' column")
    print("  2. Copy data")
    print("  3. Drop old table")
    print("  4. Rename new table")


if __name__ == "__main__":
    print("=" * 60)
    print("Migration 002: Fix Expenses Table")
    print("=" * 60)
    
    try:
        up()
        print("\n[SUCCESS] Migration completed")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
