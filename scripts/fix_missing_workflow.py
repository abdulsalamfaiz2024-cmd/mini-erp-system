import sys
import os

sys.path.insert(0, os.getcwd())

from core.database import get_db
from modules.workflow.service import WorkflowService

def fix_missing_states():
    print("Fixing missing workflow states...")
    db = get_db()
    
    # Get all sales orders
    orders = db.fetch_all("SELECT order_number FROM sales_orders")
    
    count = 0
    for o in orders:
        oid = o['order_number']
        # Check if exists in tracker
        tracker = db.fetch_one("SELECT 1 FROM document_state_tracker WHERE document_id=? AND document_type='SALES_ORDER'", (oid,))
        
        if not tracker:
            print(f"  Initializing state for {oid}...")
            try:
                WorkflowService.initialize_document_state('SALES_ORDER', oid)
                count += 1
            except Exception as e:
                print(f"  Error forcing state for {oid}: {e}")
                
    print(f"Fixed {count} orders.")

if __name__ == "__main__":
    fix_missing_states()
