"""
Setup Asset Workflow
"""

from core.database import get_db
from modules.workflow.service import WorkflowService


def setup_asset_workflow():
    """Register ASSET workflow"""
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'ASSET'")
    if existing:
        print("[OK] ASSET workflow already registered")
        return existing['workflow_id']
    
    print("[REGISTERING] Registering ASSET workflow...")
    
    # Define states
    states = [
        {'name': 'Active', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Disposed', 'sequence_order': 20, 'requires_approval': False},
    ]
    
    # Define transitions
    transitions = [
        {'from_index': 0, 'to_index': 1},  # Active → Disposed
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Asset Lifecycle",
        document_type="ASSET",
        states=states,
        transitions=transitions
    )
    
    print(f"[OK] Registered ASSET workflow: {wf_id}")
    return wf_id


if __name__ == "__main__":
    setup_asset_workflow()
