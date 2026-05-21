"""
Database Migration 001: Create Journal Entries Table
Creates the journal_entries table for accounting module
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
    
    print("[RECREATING] journal_entries table (Force)...")
    db.execute("DROP TABLE IF EXISTS journal_entry_lines")
    db.execute("DROP TABLE IF EXISTS journal_entries")
    
    db.execute("""
        CREATE TABLE journal_entries (
            entry_id TEXT PRIMARY KEY,
            entry_date DATE NOT NULL,
            description TEXT,
            reference TEXT,
            total_debit REAL DEFAULT 0,
            total_credit REAL DEFAULT 0,
            status TEXT DEFAULT 'Draft',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            posted_by INTEGER,
            posted_at TIMESTAMP,
            is_posted BOOLEAN DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (posted_by) REFERENCES users(id)
        )
    """)
    
    db.execute("""
        CREATE TABLE journal_entry_lines (
            line_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id TEXT NOT NULL,
            account_code TEXT NOT NULL,
            account_name TEXT,
            debit REAL DEFAULT 0,
            credit REAL DEFAULT 0,
            description TEXT,
            FOREIGN KEY (entry_id) REFERENCES journal_entries(entry_id)
        )
    """)
    
    print("[OK] journal_entries table created")
    print("[OK] journal_entry_lines table created")


def down():
    """Rollback migration"""
    db = get_db()
    
    print("[ROLLBACK] Dropping journal_entry_lines...")
    db.execute("DROP TABLE IF EXISTS journal_entry_lines")
    
    print("[ROLLBACK] Dropping journal_entries...")
    db.execute("DROP TABLE IF EXISTS journal_entries")
    
    print("[OK] Rollback complete")


if __name__ == "__main__":
    print("=" * 60)
    print("Migration 001: Create Journal Entries Table")
    print("=" * 60)
    
    try:
        up()
        print("\n[SUCCESS] Migration completed")
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
