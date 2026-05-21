
import sqlite3
import os
import sys

# Setup path
sys.path.append(os.getcwd())

from core.database import Database
from modules.sales.sales_manager import SalesManager
from modules.purchasing.purchasing_manager import PurchasingManager

import core.database

DB_FILE = "sales_system.db"
USER_ID = 1

def setup_test_data(db):
    # Inject into global for Managers to use
    core.database._db_instance = db
    print("Setting up test data...")
    # Create User
    # Create User (Schema: id, username, password_hash, full_name)
    db.conn.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name) VALUES (1, 'admin', 'admin_hash', 'Admin User')")
    
    # Create Customer
    db.conn.execute("INSERT OR IGNORE INTO customers (customer_id, name, email, phone) VALUES ('CUST-TEST', 'Test Customer', 'test@example.com', '123')")
    
    # Create Product (Schema matches observed: product_id, name, selling_price, cost_price) - NO stock_quantity
    db.conn.execute("INSERT OR REPLACE INTO products (product_id, name, selling_price, cost_price) VALUES ('PROD-TEST', 'Test Widget', 100.0, 50.0)")
    
    # Create Inventory (Stock initialization)
    db.conn.execute("DELETE FROM inventory WHERE product_id='PROD-TEST'") # Clean
    db.conn.execute("INSERT INTO inventory (product_id, quantity, warehouse_id) VALUES ('PROD-TEST', 1000, 1)")
    
    # Create Supplier
    db.conn.execute("INSERT OR IGNORE INTO suppliers (supplier_id, name) VALUES ('SUPP-TEST', 'Test Supplier')")
    
    db.conn.commit()

def test_sales_invoice(db):
    print("\n--- Testing Sales Invoice ---")
    
    # 1. Create Order with Tax & Discount
    items = [{
        'product_id': 'PROD-TEST',
        'quantity': 2,
        'unit_price': 100.0,
        'tax_rate': 10.0,       # 10% Tax on (200 - 0) = 20
        'discount_amount': 20.0 # $20 Discount
    }]
    # Logic: Gross = 200. Taxable = 200 - 20 = 180. Tax = 18. Total = 198.
    
    order_id = SalesManager.create_order('CUST-TEST', items, USER_ID, status='draft')
    print(f"Created Draft Order: {order_id}")
    
    # Verify DB Calculations
    row = db.fetch_one("SELECT * FROM sales_orders WHERE order_number=?", (order_id,))
    print(f"DB Totals -> Sub: {row['subtotal']}, Tax: {row['total_tax']}, Disc: {row['total_discount']}, Grand: {row['total_amount']}")
    
    assert row['subtotal'] == 200.0
    assert row['total_discount'] == 20.0, f"Expected 20 discount, got {row['total_discount']}"
    assert row['total_tax'] == 18.0, f"Expected 18 tax, got {row['total_tax']}"
    assert row['total_amount'] == 198.0
    print("[OK] Calculations Verified")
    
    # 2. Post Invoice (Confirm)
    print("Posting Invoice...")
    SalesManager.generate_invoice(order_id, USER_ID)
    
    # Verify Stock Deduction
    # prod = db.fetch_one("SELECT stock_quantity FROM products WHERE product_id='PROD-TEST'")
    inv = db.fetch_one("SELECT SUM(quantity) as qty FROM inventory WHERE product_id='PROD-TEST'")
    print(f"Stock after sale: {inv['qty']}")
    # Started with 1000. Sold 2. Should be 998.
    assert inv['qty'] == 998
    print("[OK] Stock Deduction Verified")
    
    # Verify Status
    row_updated = db.fetch_one("SELECT status FROM sales_orders WHERE order_number=?", (order_id,))
    assert 'Invoiced' in row_updated['status'].title()
    print("[OK] Status Update Verified")

def test_purchase_invoice(db):
    print("\n--- Testing Purchase Invoice ---")
    
    items = [{
        'product_id': 'PROD-TEST',
        'quantity': 10,
        'unit_price': 50.0,
        'tax_rate': 5.0,
        'discount_amount': 0.0
    }]
    # Gross 500. Tax 25. Total 525.
    
    po_id = PurchasingManager.create_purchase_order('SUPP-TEST', items, USER_ID)
    print(f"Created PO: {po_id}")
    
    r = db.fetch_one("SELECT * FROM purchase_orders WHERE po_number=?", (po_id,))
    print(f"DB Totals -> Sub: {r['subtotal']}, Tax: {r['total_tax']}, Grand: {r['total_amount']}")
    
    assert r['total_amount'] == 525.0
    print("[OK] Calculations Verified")
    
    print("Receiving Items...")
    PurchasingManager.receive_items(po_id, items, USER_ID)
    
    inv = db.fetch_one("SELECT SUM(quantity) as qty FROM inventory WHERE product_id='PROD-TEST'")
    # Started 998 (from prev test). Added 10. Should be 1008.
    print(f"Stock after receive: {inv['qty']}")
    assert inv['qty'] == 1008
    print("[OK] Stock Increase Verified")

if __name__ == "__main__":
    if os.path.exists(DB_FILE):
        # We use existing DB to test migration too? Or fresh?
        # Let's use existing.
        pass
        
    db = Database(DB_FILE)
    setup_test_data(db)
    test_sales_invoice(db)
    test_purchase_invoice(db)
    print("\nALL TESTS PASSED")
