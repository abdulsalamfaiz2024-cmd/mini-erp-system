"""
Test script for Sales Module
"""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from modules.sales.sales_manager import SalesManager
from modules.inventory.inventory_manager import InventoryManager
from core.database import get_db

def test_sales():
    print("Testing Sales Module...")
    db = get_db()
    
    # Setup Data
    cust_id = "CUST_001"
    prod_id = "PROD_001"
    user_id = 1
    
    try:
        # Create Customer
        db.conn.execute(f"INSERT OR IGNORE INTO customers (customer_id, name, current_balance) VALUES ('{cust_id}', 'Test Customer', 0)")
        db.conn.execute(f"UPDATE customers SET current_balance = 0 WHERE customer_id = '{cust_id}'")
        
        # Create Supplier & Product
        db.conn.execute("INSERT OR IGNORE INTO suppliers (supplier_id, name) VALUES ('SUP_001', 'Test Supplier')")
        db.conn.execute(f"INSERT OR IGNORE INTO products (product_id, name, supplier_id, cost_price, selling_price) VALUES ('{prod_id}', 'Test Product', 'SUP_001', 50, 100)")
        
        # Add Stock (20 units @ 50)
        db.conn.execute(f"DELETE FROM inventory WHERE product_id = '{prod_id}'") # Clear old
        InventoryManager.add_stock(prod_id, 20, 50.0, batch_number="B1")
        
        db.conn.commit()
        print("[OK] Setup Complete: Customer, Product, Stock(20)")
        
    except Exception as e:
        print(f"[ERROR] Setup failed: {e}")
        return

    # 1. Create Order
    print("\n1. Creating Sales Order...")
    try:
        items = [{'product_id': prod_id, 'quantity': 5, 'unit_price': 100.0}]
        order_number = SalesManager.create_order(cust_id, items, user_id)
        print(f"[OK] Order Created: {order_number}")
        
    except Exception as e:
        print(f"[FAIL] Create order failed: {e}")
        return

    # 2. Generate Invoice
    print("\n2. Generating Invoice...")
    try:
        SalesManager.generate_invoice(order_number, user_id)
        
        # Verify Stock Deducted
        level = InventoryManager.get_stock_level(prod_id)
        if level == 15:
            print("[OK] Stock deducted correctly (Remaining: 15)")
        else:
            print(f"[FAIL] Stock incorrect: {level}")
            
        # Verify Customer Balance Updated
        cust = db.fetch_one("SELECT current_balance FROM customers WHERE customer_id = ?", (cust_id,))
        if cust['current_balance'] == 500.0:
            print("[OK] Customer balance updated (500.0)")
        else:
            print(f"[FAIL] Customer balance incorrect: {cust['current_balance']}")
            
        # Verify Profit Calculation on Order items - wait, need to check DB
        # The SalesManager updates sales_orders total_cost/profit
        order = db.fetch_one("SELECT total_profit FROM sales_orders WHERE order_number = ?", (order_number,))
        # Cost = 5 * 50 = 250. Revenue = 5 * 100 = 500. Profit = 250.
        if order['total_profit'] == 250.0:
            print("[OK] Profit calculated correctly (250.0)")
        else:
            print(f"[FAIL] Profit calculation incorrect: {order['total_profit']}")
            
    except Exception as e:
        print(f"[FAIL] Generate invoice failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. Record Payment
    print("\n3. Recording Payment...")
    try:
        SalesManager.record_payment(order_number, 300.0, 'cash', user_id)
        
        # Verify Order Status
        order = db.fetch_one("SELECT payment_status, paid_amount, remaining_amount FROM sales_orders WHERE order_number = ?", (order_number,))
        print(f"Payment Status: {order['payment_status']}, Paid: {order['paid_amount']}, Remaining: {order['remaining_amount']}")
        
        if order['remaining_amount'] == 200.0 and order['payment_status'] == 'partial':
             print("[OK] Partial payment recorded correctly")
        else:
             print("[FAIL] Payment logic incorrect")

        # Verify Customer Balance Decreased
        cust = db.fetch_one("SELECT current_balance FROM customers WHERE customer_id = ?", (cust_id,))
        # 500 - 300 = 200
        if cust['current_balance'] == 200.0:
             print("[OK] Customer balance decreased correctly (200.0)")
        else:
             print(f"[FAIL] Customer balance incorrect after payment: {cust['current_balance']}")

    except Exception as e:
        print(f"[FAIL] Record payment failed: {e}")

if __name__ == "__main__":
    test_sales()
