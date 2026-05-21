"""
Setup Sales Return Workflow
"""

from core.database import get_db
from modules.workflow.service import WorkflowService


def setup_sales_return_workflow():
    """Register SALES_RETURN workflow"""
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'SALES_RETURN'")
    if existing:
        print("[OK] SALES_RETURN workflow already registered")
        return existing['workflow_id']
    
    print("[REGISTERING] SALES_RETURN workflow...")
    
    # Define states
    states = [
        {'name': 'Pending', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Submitted', 'sequence_order': 20, 'requires_approval': True, 'required_approval_level': 2},
        {'name': 'Approved', 'sequence_order': 30, 'requires_approval': False},
        {'name': 'Rejected', 'sequence_order': 99, 'requires_approval': False}
    ]
    
    # Define transitions
    transitions = [
        {'from_index': 0, 'to_index': 1},  # Pending → Submitted
        {'from_index': 1, 'to_index': 2},  # Submitted → Approved
        {'from_index': 1, 'to_index': 3},  # Submitted → Rejected
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Sales Return Process",
        document_type="SALES_RETURN",
        states=states,
        transitions=transitions
    )
    
    print(f"[OK] Registered SALES_RETURN workflow: {wf_id}")
    return wf_id


if __name__ == "__main__":
    setup_sales_return_workflow()
