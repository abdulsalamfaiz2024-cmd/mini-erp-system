"""
Test script for Inventory Module
"""
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from modules.inventory.inventory_manager import InventoryManager
from core.database import get_db

def test_inventory():
    print("Testing Inventory Module...")
    db = get_db()
    
    # Setup: Create a test product
    product_id = "TEST_PROD_001"
    try:
        db.conn.execute("INSERT OR IGNORE INTO suppliers (supplier_id, name) VALUES ('SUP_001', 'Test Supplier')")
        db.conn.execute(f"INSERT OR IGNORE INTO products (product_id, name, supplier_id) VALUES ('{product_id}', 'Test Product', 'SUP_001')")
        # Clear existing inventory for test
        db.conn.execute(f"DELETE FROM inventory WHERE product_id = '{product_id}'")
        db.conn.commit()
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        return

    # 1. Test Add Stock (Batch 1)
    print("\n1. Adding Stock (Batch 1)...")
    try:
        InventoryManager.add_stock(product_id, quantity=10, cost_price=100.0, batch_number="B1")
        print("[OK] Added 10 units @ 100.0")
        time.sleep(1) # Ensure timestamp diff for FIFO
    except Exception as e:
         print(f"[FAIL] Add stock failed: {e}")

    # 2. Test Add Stock (Batch 2)
    print("\n2. Adding Stock (Batch 2)...")
    try:
        InventoryManager.add_stock(product_id, quantity=5, cost_price=120.0, batch_number="B2")
        print("[OK] Added 5 units @ 120.0")
    except Exception as e:
         print(f"[FAIL] Add stock failed: {e}")

    # 3. Check Level
    level = InventoryManager.get_stock_level(product_id)
    print(f"\n3. Current Stock Level: {level}")
    if level == 15:
        print("[OK] Stock level correct (15)")
    else:
        print(f"[FAIL] Stock level incorrect (Expected 15, got {level})")

    # 4. Test Deduct Stock (FIFO)
    # Should take 10 from Batch 1 (@100) and 2 from Batch 2 (@120)
    print("\n4. Deducting 12 units (FIFO check)...")
    try:
        consumed = InventoryManager.deduct_stock(product_id, 12, user_id=1)
        
        print(f"Consumed batches: {consumed}")
        
        total_cost = sum(b['quantity'] * b['cost_price'] for b in consumed)
        expected_cost = (10 * 100.0) + (2 * 120.0) # 1000 + 240 = 1240
        
        print(f"Total Cost of Goods Sold: {total_cost}")
        
        if total_cost == expected_cost:
             print("[OK] FIFO Logic Verified (Cost matched)")
        else:
             print(f"[FAIL] FIFO Logic Failed. Expected {expected_cost}, got {total_cost}")
             
        # Check remaining
        remaining = InventoryManager.get_stock_level(product_id)
        if remaining == 3:
             print("[OK] Remaining stock correct (3)")
        else:
             print(f"[FAIL] Remaining stock incorrect (Expected 3, got {remaining})")
             
    except Exception as e:
         print(f"[FAIL] Deduct stock failed: {e}")

if __name__ == "__main__":
    test_inventory()
