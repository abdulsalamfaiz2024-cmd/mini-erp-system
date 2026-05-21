import sys
import os
import uuid
sys.path.insert(0, os.getcwd())
from core.database import get_db

def debug():
    db = get_db()
    print("Debugging FK...")
    
    # Check User
    u = db.fetch_one("SELECT * FROM users WHERE user_id=1")
    print(f"User 1: {u}")
    if not u:
        db.insert('users', {'user_id': 1, 'username': 'admin', 'password_hash': 'x', 'role': 'admin', 'status': 'active'}, return_id=False)
        print("Inserted User 1")

    # Check Emp
    emp_id = "EMP-TEST"
    try:
        db.insert('employees', {'employee_id': emp_id, 'full_name': 'Test', 'job_title': 'T', 'department': 'Sales', 'approval_level': 1, 'status': 'ACTIVE'})
    except: pass
    
    # Check Cust
    cust_id = "C-TEST"
    try:
        db.insert('customers', {'customer_id': cust_id, 'name': 'Test Cust', 'status': 'active'})
    except: pass

    # Check Sup
    sup_id = "S-TEST"
    try:
        db.insert('suppliers', {'supplier_id': sup_id, 'name': 'Sup'})
    except: pass

    # Check Prod
    prod_id = "P-TEST"
    try:
        db.insert('products', {'product_id': prod_id, 'name': 'P', 'supplier_id': sup_id, 'cost_price': 10, 'selling_price': 20})
    except Exception as e:
        print(f"Prod insert failed: {e}")

    # Try Insert Order
    try:
        db.insert('sales_orders', {
            'order_number': 'ORD-TEST',
            'customer_id': cust_id,
            'order_date': '2025-01-01',
            'status': 'Draft',
            'total_amount': 100,
            'employee_id': emp_id,
            'created_by': 1
        }, return_id=False)
        print("Order Insert Success")
    except Exception as e:
        print(f"Order Insert Failed: {e}")

    # Try Insert Item
    try:
        db.insert('sales_order_items', {
             'order_number': 'ORD-TEST',
             'product_id': prod_id,
             'quantity': 1,
             'unit_price': 10,
             'total_price': 10,
             'line_number': 1
        })
        print("Item Insert Success")
    except Exception as e:
        print(f"Item Insert Failed: {e}")

debug()
