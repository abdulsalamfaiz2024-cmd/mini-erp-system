"""
Setup Issue Order Workflow
"""

from core.database import get_db
from modules.workflow.service import WorkflowService


def setup_issue_order_workflow():
    """Register ISSUE_ORDER workflow"""
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'ISSUE_ORDER'")
    if existing:
        print("[OK] ISSUE_ORDER workflow already registered")
        return existing['workflow_id']
    
    print("[REGISTERING] Registering ISSUE_ORDER workflow...")
    
    # Define states
    states = [
        {'name': 'Pending', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Approved', 'sequence_order': 20, 'requires_approval': True, 'required_approval_level': 2},
        {'name': 'Executed', 'sequence_order': 30, 'requires_approval': False},
        {'name': 'Rejected', 'sequence_order': 99, 'requires_approval': False}
    ]
    
    # Define transitions
    transitions = [
        {'from_index': 0, 'to_index': 1},  # Pending → Approved
        {'from_index': 1, 'to_index': 2},  # Approved → Executed
        {'from_index': 0, 'to_index': 3},  # Pending → Rejected
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Issue Order Process",
        document_type="ISSUE_ORDER",
        states=states,
        transitions=transitions
    )
    
    print(f"[OK] Registered ISSUE_ORDER workflow: {wf_id}")
    return wf_id


if __name__ == "__main__":
    setup_issue_order_workflow()
