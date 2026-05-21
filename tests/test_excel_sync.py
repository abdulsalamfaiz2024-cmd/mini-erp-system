"""
Test script for Excel Integration
"""
import os
import sys
from pathlib import Path
import pandas as pd
import sqlite3

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.excel_handler import ExcelHandler, sync_excel_to_db, sync_db_to_excel
from core.database import get_db

def test_sync():
    print("Testing Excel Sync...")
    
    db = get_db()
    
    # 1. Test Import
    print("\n1. Testing Import from Excel...")
    try:
        sync_excel_to_db()
        
        # Verify customers imported
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        count = cursor.fetchone()[0]
        print(f"[OK] Imported {count} customers")
        
        # Verify first customer
        cursor.execute("SELECT * FROM customers LIMIT 1")
        row = cursor.fetchone()
        if row:
            # Avoid printing full row to preventing console encoding errors with Arabic text
            print(f"[OK] Sample Customer ID: {row['customer_id']}")#, Name: {repr(row['name'])}")
        else:
            print("[WARN] No customers found")

    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Test Export
    print("\n2. Testing Export to Excel...")
    try:
        # Create a dummy customer to export
        cursor = db.conn.cursor()
        new_customer_id = "TEST001"
        cursor.execute("""
            INSERT OR IGNORE INTO customers (customer_id, name, status) 
            VALUES (?, 'Test Export Customer', 'active')
        """, (new_customer_id,))
        db.conn.commit()
        
        sync_db_to_excel()
        
        # Verify file updated
        df = pd.read_excel('d:/sales_systems/data/customers.xlsx')
        if new_customer_id in df['customer_id'].values:
            print(f"[OK] Export verified. Found {new_customer_id} in Excel.")
        else:
            print(f"[ERROR] Export failed. {new_customer_id} not found in Excel.")
            
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sync()
