"""
Test script for Purchasing Module
"""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from modules.purchasing.purchasing_manager import PurchasingManager
from modules.inventory.inventory_manager import InventoryManager
from core.database import get_db

def test_purchasing():
    print("Testing Purchasing Module...")
    db = get_db()
    
    supplier_id = "SUP_TEST_001"
    prod_id = "PROD_TEST_001"
    user_id = 1
    
    try:
        # Setup: Ensure Supplier, Product exists
        db.conn.execute(f"INSERT OR IGNORE INTO suppliers (supplier_id, name, current_balance) VALUES ('{supplier_id}', 'Purchasing Test Supplier', 0)")
        db.conn.execute(f"UPDATE suppliers SET current_balance = 0 WHERE supplier_id = '{supplier_id}'") # Reset
        
        db.conn.execute(f"INSERT OR IGNORE INTO products (product_id, name, supplier_id, cost_price) VALUES ('{prod_id}', 'Purchasing Test Product', '{supplier_id}', 0)")
        
        # Clear Inventory
        db.conn.execute(f"DELETE FROM inventory WHERE product_id = '{prod_id}'")
        db.conn.commit()
        
        print("[OK] Setup Complete")
        
    except Exception as e:
        print(f"[FAIL] Setup failed: {e}")
        return

    # 1. Create Purchase Order
    print("\n1. Creating PO...")
    try:
        items = [{'product_id': prod_id, 'quantity': 100, 'unit_price': 10.0}]
        po_number = PurchasingManager.create_purchase_order(supplier_id, items, user_id)
        print(f"[OK] PO Created: {po_number}")
        
    except Exception as e:
        print(f"[FAIL] Create PO failed: {e}")
        return

    # 2. Receive Items
    print("\n2. Receiving Items...")
    try:
        # Received full quantity
        received_items = [{'product_id': prod_id, 'quantity': 100, 'expiry_date': '2026-12-31'}]
        PurchasingManager.receive_items(po_number, received_items, user_id)
        
        # Verify Inventory
        stock = InventoryManager.get_stock_level(prod_id)
        if stock == 100:
            print("[OK] Inventory updated correctly (100)")
        else:
            print(f"[FAIL] Inventory incorrect: {stock}")
            
        # Verify PO Status
        po = db.fetch_one("SELECT status FROM purchase_orders WHERE po_number = ?", (po_number,))
        if po['status'] == 'received':
            print("[OK] PO Status updated to 'received'")
        else:
            print(f"[FAIL] PO Status incorrect: {po['status']}")

        # Verify Supplier Balance (We owe 100 * 10 = 1000)
        supp = db.fetch_one("SELECT current_balance FROM suppliers WHERE supplier_id = ?", (supplier_id,))
        if supp['current_balance'] == 1000.0:
            print("[OK] Supplier balance updated (1000.0)")
        else:
            print(f"[FAIL] Supplier balance incorrect: {supp['current_balance']}")
            
    except Exception as e:
        print(f"[FAIL] Receive items failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Pay Supplier
    print("\n3. Paying Supplier...")
    try:
        PurchasingManager.record_payment(po_number, 600.0, 'bank', user_id)
        
        # Verify PO Payment
        po = db.fetch_one("SELECT paid_amount, remaining_amount FROM purchase_orders WHERE po_number = ?", (po_number,))
        print(f"Paid: {po['paid_amount']}, Remaining: {po['remaining_amount']}")
        
        if po['paid_amount'] == 600.0 and po['remaining_amount'] == 400.0:
            print("[OK] PO Payment recorded correctly")
        else:
            print("[FAIL] PO Payment logic incorrect")

        # Verify Supplier Balance (1000 - 600 = 400)
        supp = db.fetch_one("SELECT current_balance FROM suppliers WHERE supplier_id = ?", (supplier_id,))
        if supp['current_balance'] == 400.0:
             print("[OK] Supplier balance reduced correctly (400.0)")
        else:
             print(f"[FAIL] Supplier balance incorrect: {supp['current_balance']}")
             
    except Exception as e:
        print(f"[FAIL] Payment failed: {e}")

if __name__ == "__main__":
    test_purchasing()
