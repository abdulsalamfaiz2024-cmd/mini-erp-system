"""
Database Migration 004: Add Status Column to Expenses
Adds missing 'status' column to expenses table
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db


def up():
    """Apply migration"""
    db = get_db()
    
    # Check if status column exists
    result = db.fetch_all("PRAGMA table_info(expenses)")
    columns = [row['name'] for row in result]
    
    if 'status' in columns:
        print("[SKIP] 'status' column already exists in expenses table")
        return
    
    print("[ADDING] 'status' column to expenses table...")
    
    # Add the column with default value
    db.execute("""
        ALTER TABLE expenses 
        ADD COLUMN status TEXT DEFAULT 'approved'
    """)
    
    print("[OK] 'status' column added to expenses table")


def down():
    """Rollback migration"""
    print("[ROLLBACK] Cannot remove column in SQLite - manual intervention required")


if __name__ == "__main__":
    print("=" * 60)
    print("Migration 004: Add Status to Expenses")
    print("=" * 60)
    
    try:
        up()
        print("\n[SUCCESS] Migration completed")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
