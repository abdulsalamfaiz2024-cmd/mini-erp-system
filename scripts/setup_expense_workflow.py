"""
Setup Expense Workflow
"""

from core.database import get_db
from modules.workflow.service import WorkflowService


def setup_expense_workflow():
    """Register EXPENSE workflow"""
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'EXPENSE'")
    if existing:
        print("[OK] EXPENSE workflow already registered")
        return existing['workflow_id']
    
    print("[REGISTERING] Registering EXPENSE workflow...")
    
    # Define states
    states = [
        {'name': 'Pending_Approval', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Approved', 'sequence_order': 20, 'requires_approval': True, 'required_approval_level': 3},
        {'name': 'Rejected', 'sequence_order': 99, 'requires_approval': False}
    ]
    
    # Define transitions
    transitions = [
        {'from_index': 0, 'to_index': 1},  # Pending_Approval → Approved
        {'from_index': 0, 'to_index': 2},  # Pending_Approval → Rejected
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Expense Approval Process",
        document_type="EXPENSE",
        states=states,
        transitions=transitions
    )
    
    print(f"[OK] Registered EXPENSE workflow: {wf_id}")
    return wf_id


if __name__ == "__main__":
    setup_expense_workflow()
