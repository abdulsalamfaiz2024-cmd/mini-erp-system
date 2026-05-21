"""
Safe Data Migration Script
Migrates only matching columns from old database to new database.
"""
import sqlite3
import shutil
from datetime import datetime

# Configuration
OLD_DB = "sales_system.db"
NEW_DB = "perfect_sales_system.db"

# Tables to migrate (in order - parents first)
TABLES_TO_MIGRATE = [
    "products",
    "customers", 
    "suppliers",
    "inventory",
    "sales_orders",
    "sales_order_items",
    "purchase_orders",
    "purchase_order_items",
    "payments",
]

def get_columns(cursor, table):
    """Get column names for a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    return [col[1] for col in cursor.fetchall()]

def migrate_table(old_cursor, new_cursor, table):
    """Migrate only matching columns from old to new table"""
    
    # Get columns from both tables
    old_cols = set(get_columns(old_cursor, table))
    new_cols = set(get_columns(new_cursor, table))
    
    # Find common columns
    common_cols = list(old_cols & new_cols)
    
    if not common_cols:
        print(f"  SKIP: No common columns for {table}")
        return 0
    
    # Build query
    cols_str = ", ".join(common_cols)
    placeholders = ", ".join(["?" for _ in common_cols])
    
    # Fetch data from old database
    old_cursor.execute(f"SELECT {cols_str} FROM {table}")
    rows = old_cursor.fetchall()
    
    if not rows:
        print(f"  SKIP: No data in old {table}")
        return 0
    
    # Insert into new database (skip duplicates)
    inserted = 0
    skipped = 0
    
    for row in rows:
        try:
            new_cursor.execute(
                f"INSERT OR IGNORE INTO {table} ({cols_str}) VALUES ({placeholders})",
                row
            )
            if new_cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except sqlite3.Error as e:
            print(f"    Error inserting row: {e}")
            skipped += 1
    
    return inserted, skipped

def run_migration():
    """Run the safe migration"""
    print("=" * 60)
    print("SAFE DATA MIGRATION")
    print(f"From: {OLD_DB} -> To: {NEW_DB}")
    print(f"Started: {datetime.now()}")
    print("=" * 60)
    
    # Connect to databases
    old_conn = sqlite3.connect(OLD_DB)
    new_conn = sqlite3.connect(NEW_DB)
    
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()
    
    results = []
    
    for table in TABLES_TO_MIGRATE:
        print(f"\nMigrating: {table}")
        
        # Check if table exists in both
        old_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not old_cursor.fetchone():
            print(f"  SKIP: Table not in old database")
            continue
            
        new_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not new_cursor.fetchone():
            print(f"  SKIP: Table not in new database")
            continue
        
        result = migrate_table(old_cursor, new_cursor, table)
        if isinstance(result, tuple):
            inserted, skipped = result
            print(f"  DONE: {inserted} inserted, {skipped} skipped (duplicates)")
            results.append((table, inserted, skipped))
    
    # Commit changes
    new_conn.commit()
    
    # Close connections
    old_conn.close()
    new_conn.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)
    
    total_inserted = 0
    for table, inserted, skipped in results:
        print(f"  {table}: {inserted} records")
        total_inserted += inserted
    
    print(f"\nTotal records migrated: {total_inserted}")
    print(f"Backup saved as: perfect_sales_system_backup_before_migration.db")
    
    return total_inserted

if __name__ == "__main__":
    run_migration()
