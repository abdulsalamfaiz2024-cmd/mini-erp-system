"""
Setup Journal Entry Workflow
"""

from core.database import get_db
from modules.workflow.service import WorkflowService


def setup_journal_workflow():
    """Register JOURNAL_ENTRY workflow"""
    db = get_db()
    
    # Check if exists
    existing = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'JOURNAL_ENTRY'")
    if existing:
        print("[OK] JOURNAL_ENTRY workflow already registered")
        return existing['workflow_id']
    
    print("[REGISTERING] Registering JOURNAL_ENTRY workflow...")
    
    # Define states
    states = [
        {'name': 'Unposted', 'sequence_order': 10, 'requires_approval': False},
        {'name': 'Posted', 'sequence_order': 20, 'requires_approval': False},
    ]
    
    # Define transitions
    transitions = [
        {'from_index': 0, 'to_index': 1},  # Unposted → Posted
    ]
    
    wf_id = WorkflowService.register_workflow(
        name="Journal Entry Posting",
        document_type="JOURNAL_ENTRY",
        states=states,
        transitions=transitions
    )
    
    print(f"[OK] Registered JOURNAL_ENTRY workflow: {wf_id}")
    return wf_id


if __name__ == "__main__":
    setup_journal_workflow()
