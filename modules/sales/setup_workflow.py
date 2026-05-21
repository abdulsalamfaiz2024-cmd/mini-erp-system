from core.database import get_db
from modules.workflow.service import WorkflowService

def setup_sales_workflow():
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'SALES_ORDER'")
    if existing:
        print("Cleaning up old 'SALES_ORDER' workflow...")
        # Tracker
        db.execute("DELETE FROM document_state_tracker WHERE document_type = 'SALES_ORDER'")
        # Transitions & States
        old_states = db.fetch_all("SELECT state_id FROM workflow_states WHERE workflow_id = ?", (existing['workflow_id'],))
        for s in old_states:
             db.execute("DELETE FROM workflow_transitions WHERE from_state_id = ? OR to_state_id = ?", (s['state_id'], s['state_id']))
             db.execute("DELETE FROM approval_records WHERE state_id = ?", (s['state_id'],))
        db.execute("DELETE FROM workflow_states WHERE workflow_id = ?", (existing['workflow_id'],))
        db.execute("DELETE FROM workflow_definitions WHERE workflow_id = ?", (existing['workflow_id'],))

    print("Registering 'Standard Sales Lifecycle'...")
    
    # Define States
    states = [
        {'name': 'Draft', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Submitted', 'sequence_order': 20, 'requires_approval': True, 'required_approval_level': 3}, # Requires Finance (Level 3) to advance
        {'name': 'Finance_Approved', 'sequence_order': 30, 'requires_approval': True, 'required_approval_level': 3}, # Requires Manager/Lead to advance
        {'name': 'Ready_For_Warehouse', 'sequence_order': 40, 'requires_approval': True, 'required_approval_level': 2}, # Warehouse Lead (Level 2) to advance
        {'name': 'Completed', 'sequence_order': 50, 'requires_approval': False},
        {'name': 'Rejected', 'sequence_order': 99, 'requires_approval': False}
    ]
    
    # Define Transitions (Indices based on states list)
    # 0: Draft, 1: Submitted, 2: Finance, 3: Warehouse, 4: Completed, 5: Rejected
    transitions = [
        {'from_index': 0, 'to_index': 1}, # Draft -> Submitted
        {'from_index': 1, 'to_index': 2}, # Submitted -> Finance_Approved
        {'from_index': 2, 'to_index': 3}, # Finance -> Warehouse
        {'from_index': 3, 'to_index': 4}, # Warehouse -> Completed
        # Rejections
        {'from_index': 1, 'to_index': 5}, # Submitted -> Rejected
        {'from_index': 2, 'to_index': 5}, # Finance -> Rejected
        {'from_index': 3, 'to_index': 5}, # Warehouse -> Rejected
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Standard Sales Lifecycle",
        document_type="SALES_ORDER",
        states=states,
        transitions=transitions
    )
    print(f"Workflow Registered: {wf_id}")
    return wf_id

if __name__ == "__main__":
    setup_sales_workflow()
