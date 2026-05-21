import sys
import os

sys.path.insert(0, os.getcwd())

from core.database import get_db

def sync_status():
    print("Syncing Legacy Status with Workflow State...")
    db = get_db()
    
    sql = """
        SELECT so.order_number, ws.name as wf_state
        FROM sales_orders so
        JOIN document_state_tracker dst ON dst.document_id = so.order_number
        JOIN workflow_states ws ON dst.current_state_id = ws.state_id
        WHERE dst.document_type = 'SALES_ORDER'
    """
    rows = db.fetch_all(sql)
    
    mapping = {
        'Draft': 'draft',
        'Submitted': 'submitted',
        'Finance_Approved': 'approved',
        'Ready_For_Warehouse': 'approved', 
        'Completed': 'completed',
        'Rejected': 'rejected'
    }
    
    count = 0
    for r in rows:
        oid = r['order_number']
        state = r['wf_state']
        new_status = mapping.get(state, 'draft')
        
        # Check current
        curr = db.fetch_one("SELECT status FROM sales_orders WHERE order_number=?", (oid,))['status']
        
        if curr != new_status:
            print(f"  Updating {oid}: {curr} -> {new_status} ({state})")
            db.execute("UPDATE sales_orders SET status=? WHERE order_number=?", (new_status, oid))
            count += 1
            
    print(f"Synced {count} orders.")

if __name__ == "__main__":
    sync_status()
