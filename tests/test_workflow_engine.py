import sys
import os
import uuid
from datetime import datetime

# Setup path
sys.path.insert(0, os.getcwd())

from core.database import get_db, close_db
from modules.workflow.service import WorkflowService, ApprovalService

def setup_test_data():
    db = get_db()
    
    # 1. Create Employees with different levels
    junior_id = str(uuid.uuid4())
    senior_id = str(uuid.uuid4())
    
    db.insert('employees', {
        'employee_id': junior_id,
        'full_name': 'Junior Approver',
        'job_title': 'Jr',
        'department': 'Sales',
        'approval_level': 1,
        'status': 'ACTIVE',
        'user_id': None 
    })
    
    db.insert('employees', {
        'employee_id': senior_id,
        'full_name': 'Senior Director',
        'job_title': 'Sr',
        'department': 'Sales',
        'approval_level': 5,
        'status': 'ACTIVE',
        'user_id': None
    })
    
    return junior_id, senior_id

def test_workflow():
    print("--- Starting Workflow Engine Test ---")
    
    # Cleaning up previous test runs
    db = get_db()
    
    # Manually delete children first because of strict FKs
    # 1. State Tracker (FK to States)
    tracker_rows = db.fetch_all("SELECT tracker_id FROM document_state_tracker WHERE document_type = 'TEST_ORDER'")
    if tracker_rows:
        db.execute("DELETE FROM document_state_tracker WHERE document_type = 'TEST_ORDER'")

    # 2. Workflow Definitions (Cascades to States, but safe to delete states first explicitly)
    wf_def = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = 'TEST_ORDER'")
    if wf_def:
        # Delete Approval Records (FK to States, FK to Employees)
        # We need to find states first
        states = db.fetch_all("SELECT state_id FROM workflow_states WHERE workflow_id = ?", (wf_def['workflow_id'],))
        for s in states:
            db.execute("DELETE FROM approval_records WHERE state_id = ?", (s['state_id'],))
            
        # Now delete def
        db.execute("DELETE FROM workflow_definitions WHERE workflow_id = ?", (wf_def['workflow_id'],))
        
    # 1. Register Workflow
    print("[1] Registering 'Sales Order Test' Workflow...")
    wf_id = WorkflowService.register_workflow(
        name="Sales Order Test",
        document_type="TEST_ORDER",
        states=[
            {'name': 'Draft', 'sequence_order': 1, 'requires_approval': False},
            {'name': 'Manager Approval', 'sequence_order': 2, 'requires_approval': True, 'required_approval_level': 1},
            {'name': 'Director Approval', 'sequence_order': 3, 'requires_approval': True, 'required_approval_level': 5},
            {'name': 'Completed', 'sequence_order': 4, 'requires_approval': False}
        ]
    )
    print(f"    Success. Workflow ID: {wf_id}")
    
    # 2. Initialize Document
    doc_id = "DOC-001"
    print(f"[2] Initializing Document {doc_id}...")
    WorkflowService.initialize_document_state("TEST_ORDER", doc_id)
    
    state = WorkflowService.get_current_state("TEST_ORDER", doc_id)
    print(f"    Current State: {state['name']} (Order {state['sequence_order']})")
    assert state['name'] == 'Draft'
    
    # 3. Junior advances Draft -> Manager Approval (No approval needed for Draft -> Manager? Wait, logic check)
    # Draft state has requires_approval=False. So `approve_document` logic:
    # If current state !requires_approval, does approve_document move it?
    # Yes, typically "submit" action. We use `approve_document` for generic advancement here for simplicity or add `advance` method?
    # Service implementation uses `approve_document` to check permissions AND advance. 
    # If requires_approval is False, we typically just need ANY valid user to advance.
    
    junior_id, senior_id = setup_test_data()
    
    print("[3] Advancing Draft -> Manager Approval...")
    ApprovalService.approve_document("TEST_ORDER", doc_id, junior_id, "Submitting draft")
    state = WorkflowService.get_current_state("TEST_ORDER", doc_id)
    print(f"    Current State: {state['name']}")
    assert state['name'] == 'Manager Approval'
    
    # 4. Junior tries to approve 'Manager Approval' (Level 1 req, Junior has Level 1)
    print("[4] High approval test (Manager Approval)...")
    ApprovalService.approve_document("TEST_ORDER", doc_id, junior_id, "Manager OK")
    state = WorkflowService.get_current_state("TEST_ORDER", doc_id)
    print(f"    Current State: {state['name']}")
    assert state['name'] == 'Director Approval'
    
    # 5. Junior tries to approve 'Director Approval' (Level 5 req, Junior has Level 1) -> SHOULD FAIL
    print("[5] Junior attempting Director Approval (Should Fail)...")
    try:
        ApprovalService.approve_document("TEST_ORDER", doc_id, junior_id)
        print("    FAILURE: Junior was allowed to approve!")
    except PermissionError as e:
        print(f"    SUCCESS: Blocked - {e}")
        
    # 6. Senior approves 'Director Approval' -> Success
    print("[6] Senior attempting Director Approval...")
    ApprovalService.approve_document("TEST_ORDER", doc_id, senior_id, "Director OK")
    state = WorkflowService.get_current_state("TEST_ORDER", doc_id)
    print(f"    Current State: {state['name']}")
    assert state['name'] == 'Completed'

    print("--- ALL TESTS PASSED ---")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
