from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    document_type: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class WorkflowState:
    state_id: Optional[int]
    workflow_id: str
    name: str
    sequence_order: int
    requires_approval: bool = False
    required_approval_level: int = 0
    department: Optional[str] = None

@dataclass
class WorkflowTransition:
    transition_id: Optional[int]
    from_state_id: int
    to_state_id: int
    allowed_role: Optional[str] = None
    created_at: Optional[datetime] = None

@dataclass
class ApprovalRecord:
    approval_id: Optional[int]
    document_type: str
    document_id: str
    state_id: int
    approved_by_employee_id: str
    approval_action: str  # 'APPROVED', 'REJECTED'
    comment: Optional[str] = None
    approved_at: Optional[datetime] = None

@dataclass
class DocumentStateTracker:
    tracker_id: Optional[int]
    document_type: str
    document_id: str
    current_state_id: int
    version: int = 1 # Optimistic Locking
    last_updated_at: Optional[datetime] = None
