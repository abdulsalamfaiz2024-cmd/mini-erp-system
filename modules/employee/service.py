"""
Employee Service Layer
Handles business logic, validation, and database operations for Employees.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from core.database import get_db, DatabaseError
from core.logger import get_logger
from core.validators import ValidationError
from modules.employee.models import Employee
from modules.employee.constants import EmployeeStatus
from modules.security.audit import AuditLogger

logger = get_logger('employee_service')

class EmployeeService:
    """
    Service for managing Employee lifecycle and permissions.
    """

    @staticmethod
    def _map_row_to_employee(row: Any) -> Employee:
        """Map database row to Employee object"""
        if not row:
            return None
        
        # Convert DB integer booleans to Python booleans
        return Employee(
            employee_id=row['employee_id'],
            full_name=row['full_name'],
            job_title=row['job_title'],
            department=row['department'],
            status=EmployeeStatus(row['status']),
            hire_date=date.fromisoformat(row['hire_date']) if row['hire_date'] else None,
            contact_email=row['contact_email'],
            contact_phone=row['contact_phone'],
            can_create_orders=bool(row['can_create_orders']),
            can_approve_orders=bool(row['can_approve_orders']),
            can_release_inventory=bool(row['can_release_inventory']),
            can_post_accounting=bool(row['can_post_accounting']),
            approval_level=row['approval_level'],
            user_id=row['user_id'],
            created_by_employee_id=row['created_by_employee_id'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
        )

    @staticmethod
    def create_employee(data: Dict[str, Any], performed_by_id: Optional[str] = None) -> str:
        """
        Create a new employee.
        
        Args:
            data: Employee data dictionary
            performed_by_id: ID of employee performing the action (for audit)
            
        Returns:
            New employee_id
        """
        db = get_db()
        try:
            # Validate required fields
            required = ['full_name', 'job_title', 'department']
            for field in required:
                if not data.get(field):
                    raise ValidationError(f"Field '{field}' is required")

            employee_id = str(uuid.uuid4())
            
            # Default values
            default_status = EmployeeStatus.ACTIVE.value
            
            with db.transaction() as cursor:
                db.insert('employees', {
                    'employee_id': employee_id,
                    'full_name': data['full_name'],
                    'job_title': data['job_title'],
                    'department': data['department'],
                    'status': default_status,
                    'hire_date': data.get('hire_date'),
                    'contact_email': data.get('contact_email'),
                    'contact_phone': data.get('contact_phone'),
                    
                    # Permissions (defaults to False if not provided)
                    'can_create_orders': 1 if data.get('can_create_orders') else 0,
                    'can_approve_orders': 1 if data.get('can_approve_orders') else 0,
                    'can_release_inventory': 1 if data.get('can_release_inventory') else 0,
                    'can_post_accounting': 1 if data.get('can_post_accounting') else 0,
                    'approval_level': data.get('approval_level'),
                    
                    'created_by_employee_id': performed_by_id,
                    'user_id': data.get('user_id') # Optional link on creation
                })
                
                # We need to adapt AuditLogger to handle employee_id or map it.
                # Current AuditLogger uses 'user_id' (integer).
                # If performed_by_id is provided (UUID), we might need to look up the user_id or just log it in notes.
                # Ideally audit_logs should have performed_by_employee_id, but schema doesn't have it yet.
                # For Phase 1, we will log using available mechanisms or just log to text if DB not ready.
                # Based on audit.py, it takes user_id (int).
                
                # TODO: Update AuditLogger to support employee_id. For now, we log generically.
                
            logger.info(f"Created employee {employee_id}")
            return employee_id

        except Exception as e:
            logger.error(f"Failed to create employee: {e}")
            raise

    @staticmethod
    def get_employee(employee_id: str) -> Optional[Employee]:
        """Get employee by ID"""
        db = get_db()
        row = db.fetch_one("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
        return EmployeeService._map_row_to_employee(row)

    @staticmethod
    def update_employee(employee_id: str, data: Dict[str, Any], performed_by_id: Optional[str] = None) -> bool:
        """Update employee details"""
        db = get_db()
        try:
            # Check existence
            current = EmployeeService.get_employee(employee_id)
            if not current:
                raise ValidationError(f"Employee {employee_id} not found")
            
            # Cannot update if archived (unless un-archiving? Rules say Read-Only)
            if current.status == EmployeeStatus.ARCHIVED:
                raise ValidationError("Cannot update ARCHIVED employee")

            allowed_fields = [
                'full_name', 'job_title', 'department', 'contact_email', 'contact_phone',
                'hire_date', 'user_id', 'approval_level'
            ]
            
            updates = {k: v for k, v in data.items() if k in allowed_fields}
            updates['updated_at'] = datetime.now()
            
            if not updates:
                return False
                
            db.update('employees', updates, 'employee_id = ?', (employee_id,))
            logger.info(f"Updated employee {employee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update employee {employee_id}: {e}")
            raise

    @staticmethod
    def change_status(employee_id: str, new_status: EmployeeStatus, performed_by_id: Optional[str] = None):
        """Change employee status (SUSPEND, ARCHIVE, ACTIVATE)"""
        db = get_db()
        try:
             # Check existence
            current = EmployeeService.get_employee(employee_id)
            if not current:
                raise ValidationError(f"Employee {employee_id} not found")
            
            db.update('employees', {
                'status': new_status.value,
                'updated_at': datetime.now()
            }, 'employee_id = ?', (employee_id,))
            
            logger.info(f"Changed status of {employee_id} to {new_status.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to change status for {employee_id}: {e}")
            raise

    @staticmethod
    def assign_permissions(employee_id: str, permissions: Dict[str, bool], performed_by_id: Optional[str] = None):
        """Update operational permissions"""
        db = get_db()
        try:
             # Check existence
            current = EmployeeService.get_employee(employee_id)
            if not current:
                raise ValidationError(f"Employee {employee_id} not found")
                
            if current.status != EmployeeStatus.ACTIVE:
                 raise ValidationError("Cannot assign permissions to non-ACTIVE employee")

            valid_perms = ['can_create_orders', 'can_approve_orders', 'can_release_inventory', 'can_post_accounting']
            updates = {}
            for k, v in permissions.items():
                if k in valid_perms:
                    updates[k] = 1 if v else 0
            
            if not updates:
                return False
                
            updates['updated_at'] = datetime.now()
            db.update('employees', updates, 'employee_id = ?', (employee_id,))
            
            logger.info(f"Updated permissions for {employee_id}")
            return True
        except Exception as e:
             logger.error(f"Failed to update permissions for {employee_id}: {e}")
             raise

    @staticmethod
    def list_employees(active_only: bool = True) -> List[Employee]:
        """List employees"""
        db = get_db()
        query = "SELECT * FROM employees"
        if active_only:
            query += " WHERE status = 'ACTIVE'"
        
        rows = db.fetch_all(query)
        return [EmployeeService._map_row_to_employee(row) for row in rows]
