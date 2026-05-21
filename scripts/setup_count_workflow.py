"""
Setup Inventory Count Workflow
"""

from core.database import get_db
from modules.workflow.service import WorkflowService


def setup_inventory_count_workflow():
    """Register INVENTORY_COUNT workflow"""
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'INVENTORY_COUNT'")
    if existing:
        print("[OK] INVENTORY_COUNT workflow already registered")
        return existing['workflow_id']
    
    print("[REGISTERING] Registering INVENTORY_COUNT workflow...")
    
    # Define states
    states = [
        {'name': 'In_Progress', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Submitted', 'sequence_order': 20, 'requires_approval': True, 'required_approval_level': 3},
        {'name': 'Approved', 'sequence_order': 30, 'requires_approval': False},
        {'name': 'Rejected', 'sequence_order': 99, 'requires_approval': False}
    ]
    
    # Define transitions
    transitions = [
        {'from_index': 0, 'to_index': 1},  # In_Progress → Submitted
        {'from_index': 1, 'to_index': 2},  # Submitted → Approved
        {'from_index': 1, 'to_index': 3},  # Submitted → Rejected
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Inventory Count Process",
        document_type="INVENTORY_COUNT",
        states=states,
        transitions=transitions
    )
    
    print(f"[OK] Registered INVENTORY_COUNT workflow: {wf_id}")
    return wf_id


if __name__ == "__main__":
    setup_inventory_count_workflow()
