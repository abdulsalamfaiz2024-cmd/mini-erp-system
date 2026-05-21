"""
Test script for CRM Module
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from modules.crm.crm_manager import CRMManager
from core.database import get_db

def test_crm():
    print("Testing CRM Module...")
    db = get_db()
    
    cust_id = "CRM_TEST_CUST"
    
    # Setup Data
    try:
        # Create Customer with credit limit
        db.conn.execute(f"INSERT OR IGNORE INTO customers (customer_id, name, credit_limit, current_balance) VALUES ('{cust_id}', 'CRM Test Customer', 1000, 500)")
        # Insert a dummy order
        db.conn.execute(f"INSERT OR IGNORE INTO sales_orders (order_number, customer_id, total_amount, order_date, status) VALUES ('SO-CRM-001', '{cust_id}', 2000, '2025-12-14', 'invoiced')")
        db.conn.commit()
    except Exception as e:
        print(f"[FAIL] Setup failed: {e}")
        return

    # 1. Check History
    print("\n1. Checking History...")
    try:
        hist = CRMManager.get_customer_history(cust_id)
        print(f"History Items: {len(hist)}")
        if len(hist) >= 1:
            print("[OK] History retrieved")
        else:
            print("[FAIL] History empty")
    except Exception as e:
         print(f"[FAIL] History check failed: {e}")

    # 2. Check Segmentation
    print("\n2. Checking Segmentation...")
    try:
        segs = CRMManager.get_customer_segmentation()
        # Find our customer
        c = next((x for x in segs if x['customer_id'] == cust_id), None)
        if c:
            print(f"Customer Segment: {c['segment']} (Spent: {c['total_spent']})")
            # Spent 2000 -> Silver (>1000) or Gold (>5000)
            if c['segment'] == 'Silver':
                print("[OK] Segmentation Logic Correct")
            else:
                print(f"[INFO] Segment is {c['segment']}")
        else:
             print("[FAIL] Customer not found in segmentation")
    except Exception as e:
         print(f"[FAIL] Segmentation failed: {e}")

    # 3. Credit Limit Check
    print("\n3. Credit Limit Check...")
    try:
        # Balance is 500. Limit is 1000. Available 500.
        
        # Try adding 400 (Should pass)
        if CRMManager.check_credit_limit(cust_id, 400):
            print("[OK] Credit check passed for 400")
        else:
             print("[FAIL] Credit check failed for 400 (Should pass)")
             
        # Try adding 600 (Total 1100 > 1000 -> Fail)
        if not CRMManager.check_credit_limit(cust_id, 600):
             print("[OK] Credit check failed correctly for 600")
        else:
             print("[FAIL] Credit check passed for 600 (Should fail)")
             
    except Exception as e:
         print(f"[FAIL] Credit check failed: {e}")

if __name__ == "__main__":
    test_crm()
