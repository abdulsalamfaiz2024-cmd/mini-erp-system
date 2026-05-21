from typing import List, Optional, Dict, Any
from core.database import get_db, DatabaseError
from modules.workflow.models import WorkflowDefinition, WorkflowState, ApprovalRecord, DocumentStateTracker
from datetime import datetime
import uuid

class WorkflowError(Exception):
    """Base class for workflow errors"""
    pass

class ConcurrentModificationError(WorkflowError):
    """Raised when optimistic locking fails"""
    pass

class WorkflowService:
    @staticmethod
    def register_workflow(name: str, document_type: str, states: List[Dict[str, Any]], transitions: List[Dict[str, Any]] = None) -> str:
        """
        Register a new workflow definition with states and Explicit Transitions.
        Args:
            states: List of dicts like {'name': 'Draft', ...}
            transitions: List of dicts like {'from_index': 0, 'to_index': 1}
        """
        db = get_db()
        workflow_id = str(uuid.uuid4())
        
        with db.transaction():
            # Create Definition
            db.insert('workflow_definitions', {
                'workflow_id': workflow_id,
                'name': name,
                'document_type': document_type,
                'is_active': 1
            })
            
            # Create States
            state_ids = []
            for s in states:
                sid = db.insert('workflow_states', {
                    'workflow_id': workflow_id,
                    'name': s['name'],
                    'sequence_order': s['sequence_order'],
                    'requires_approval': 1 if s.get('requires_approval') else 0,
                    'required_approval_level': s.get('required_approval_level', 0),
                    'department': s.get('department')
                })
                state_ids.append(sid)
            
            # Auto-create linear transitions if none provided (Backward Compatibility)
            if not transitions:
                for i in range(len(state_ids) - 1):
                    db.insert('workflow_transitions', {
                        'from_state_id': state_ids[i],
                        'to_state_id': state_ids[i+1]
                    })
            else:
                for t in transitions:
                    db.insert('workflow_transitions', {
                        'from_state_id': state_ids[t['from_index']],
                        'to_state_id': state_ids[t['to_index']]
                    })
                
        return workflow_id

    @staticmethod
    def get_workflow_for_type(document_type: str) -> Optional[str]:
        db = get_db()
        row = db.fetch_one("SELECT workflow_id FROM workflow_definitions WHERE document_type = ? AND is_active = 1", (document_type,))
        return row['workflow_id'] if row else None

    @staticmethod
    def initialize_document_state(document_type: str, document_id: str):
        """Sets the document to the first state of its workflow"""
        workflow_id = WorkflowService.get_workflow_for_type(document_type)
        if not workflow_id:
            # OPTIONAL: If no workflow defined, do we error or allow?
            # Remediation Requirement: "Sales Order save... MUST FAIL if No workflow attached"
            raise WorkflowError(f"No active workflow found for {document_type}")
            
        db = get_db()
        # Get first state
        first_state = db.fetch_one("""
            SELECT state_id FROM workflow_states 
            WHERE workflow_id = ? 
            ORDER BY sequence_order ASC LIMIT 1
        """, (workflow_id,))
        
        if not first_state:
            raise WorkflowError("Workflow has no states")
            
        try:
            db.insert('document_state_tracker', {
                'document_type': document_type,
                'document_id': document_id,
                'current_state_id': first_state['state_id'],
                'version': 1,
                'last_updated_at': datetime.now()
            })
        except DatabaseError:
            # Already initialized
            pass

    @staticmethod
    def get_current_state(document_type: str, document_id: str) -> Optional[dict]:
        db = get_db()
        # Fetch version too
        row = db.fetch_one("""
            SELECT s.*, t.version as tracker_version, t.tracker_id
            FROM document_state_tracker t
            JOIN workflow_states s ON t.current_state_id = s.state_id
            WHERE t.document_type = ? AND t.document_id = ?
        """, (document_type, document_id))
        return dict(row) if row else None
        
    @staticmethod
    def get_next_state(current_state_id: int) -> Optional[dict]:
        """Using Explicit Transitions Table"""
        db = get_db()
        # Find transition
        transition = db.fetch_one("""
            SELECT to_state_id FROM workflow_transitions
            WHERE from_state_id = ?
            LIMIT 1
        """, (current_state_id,))
        
        if not transition: return None
        
        # Get State Details
        state = db.fetch_one("SELECT * FROM workflow_states WHERE state_id = ?", (transition['to_state_id'],))
        return dict(state) if state else None


class ApprovalService:
    @staticmethod
    def approve_document(document_type: str, document_id: str, employee_id: str, comment: str = None):
        db = get_db()
        
        # 1. Get Current State & Version (Read Phase)
        current_state = WorkflowService.get_current_state(document_type, document_id)
        if not current_state:
            raise WorkflowError("Document not tracked in workflow")
            
        # 2. Check Permissions
        approver = db.fetch_one("SELECT approval_level, status FROM employees WHERE employee_id = ?", (employee_id,))
        if not approver or approver['status'] != 'ACTIVE':
            raise PermissionError("Approver is not active or invalid")
            
        if current_state['requires_approval']:
            required_level = current_state['required_approval_level']
            if (approver['approval_level'] or 0) < required_level:
                raise PermissionError(f"Insufficient Approval Level. Required: {required_level}, Has: {approver['approval_level']}")

        # 3. Check for Duplicate Approval
        # If user has already approved THIS state for THIS doc? 
        # (Though duplicate approval usually means multiple people acting on same state)
        if db.fetch_one("SELECT 1 FROM approval_records WHERE document_type=? AND document_id=? AND state_id=? AND approved_by_employee_id=?", 
                       (document_type, document_id, current_state['state_id'], employee_id)):
             raise WorkflowError("User already approved this state")

        # 4. Perform Transition with Optimistic Locking
        with db.transaction():
            # Record Approval
            db.insert('approval_records', {
                'document_type': document_type,
                'document_id': document_id,
                'state_id': current_state['state_id'],
                'approved_by_employee_id': employee_id,
                'approval_action': 'APPROVED',
                'comment': comment,
                'approved_at': datetime.now()
            })
            
            # Advance State
            next_state = WorkflowService.get_next_state(current_state['state_id'])
            if next_state:
                # OPTIMISTIC LOCKING UPDATE
                # Update ONLY IF version matches what we read
                curr_version = current_state['tracker_version']
                updated_rows = db.update(
                    'document_state_tracker', 
                    {
                        'current_state_id': next_state['state_id'], 
                        'last_updated_at': datetime.now(),
                        'version': curr_version + 1
                    },
                    "document_type = ? AND document_id = ? AND version = ?",
                    (document_type, document_id, curr_version)
                )
                
                if updated_rows == 0:
                    raise ConcurrentModificationError("State changed by another transaction. Please refresh.")
            else:
                # Final State - Just update timestamp/version? 
                # Or do nothing? Ideally we should update version to signal activity
                pass

    @staticmethod
    def reject_document(document_type: str, document_id: str, employee_id: str, reason: str):
        db = get_db()
        current_state = WorkflowService.get_current_state(document_type, document_id)
        if not current_state: raise WorkflowError("Document not tracked")
            
        with db.transaction():
             db.insert('approval_records', {
                'document_type': document_type,
                'document_id': document_id,
                'state_id': current_state['state_id'],
                'approved_by_employee_id': employee_id,
                'approval_action': 'REJECTED',
                'comment': reason,
                'approved_at': datetime.now()
            })
             
             # Phase 3 Update: Move to 'Rejected' state if available
             rejected_state = db.fetch_one("SELECT state_id FROM workflow_states WHERE workflow_id = ? AND name = 'Rejected'", (current_state['workflow_id'],))
             if rejected_state:
                 curr_version = current_state['tracker_version']
                 db.update(
                    'document_state_tracker', 
                    {
                        'current_state_id': rejected_state['state_id'], 
                        'last_updated_at': datetime.now(),
                        'version': curr_version + 1
                    },
                    "document_type = ? AND document_id = ? AND version = ?",
                    (document_type, document_id, curr_version)
                )
