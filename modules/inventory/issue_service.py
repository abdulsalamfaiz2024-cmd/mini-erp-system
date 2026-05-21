"""
Issue Order Service (Warehouse Stock Issues)
Handles warehouse stock issue workflow linked to sales orders
"""

from typing import List, Dict
from datetime import datetime
from core.database import get_db
from core.logger import get_logger
from core.validators import ValidationError
from modules.workflow.service import WorkflowService, ApprovalService
from modules.inventory.inventory_manager import InventoryManager
from modules.security.audit import AuditLogger

logger = get_logger('issue_orders')


class IssueOrderService:
    """Manages warehouse issue orders"""
    
    @staticmethod
    def create_issue(sales_order_id: str, items: List[Dict], employee_id: str,
                    user_id: int) -> str:
        """
        Create an issue order (request to release stock for sales order).
        
        Args:
            sales_order_id: Linked sales order
            items: [{'product_id': str, 'quantity': int}]
            employee_id: Employee creating issue
            user_id: User ID
        
        Returns:
            issue_id
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Validate sales order
                order = db.fetch_one(
                    "SELECT * FROM sales_orders WHERE order_number=?",
                    (sales_order_id,)
                )
                
                if not order:
                    raise ValidationError(f"Sales order {sales_order_id} not found")
                
                # Generate issue ID
                date_str = datetime.now().strftime('%Y%m%d')
                row = db.fetch_one("SELECT MAX(id) as max_id FROM issue_orders")
                new_id_num = (row['max_id'] or 0) + 1
                issue_id = f"ISS-{date_str}-{new_id_num:04d}"
                
                # Create issue header
                db.insert('issue_orders', {
                    'issue_id': issue_id,
                    'sales_order_id': sales_order_id,
                    'issue_date': datetime.now().date().isoformat(),
                    'status': 'pending',
                    'created_by': employee_id
                })
                
                # Create issue lines
                for item in items:
                    # Check stock availability
                    if not InventoryManager.check_stock_availability(item['product_id'], item['quantity']):
                        raise ValidationError(f"Insufficient stock for {item['product_id']}")
                    
                    db.insert('issue_order_items', {
                        'issue_id': issue_id,
                        'product_id': item['product_id'],
                        'quantity': item['quantity']
                    })
                
                # Initialize workflow
                WorkflowService.initialize_document_state('ISSUE_ORDER', issue_id)
                
                AuditLogger.log(user_id, 'CREATE_ISSUE', 'issue_orders', issue_id,
                              new_value=f"SO:{sales_order_id}")
                
                logger.info(f"Created issue order {issue_id} for SO {sales_order_id}")
                return issue_id
                
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            raise
    
    @staticmethod
    def approve_issue(issue_id: str, approver_employee_id: str):
        """
        Approve issue order (warehouse supervisor approval).
        
        Args:
            issue_id: Issue order ID
            approver_employee_id: Approving employee
        """
        try:
            ApprovalService.approve_document(
                "ISSUE_ORDER", issue_id, approver_employee_id, "Issue approved"
            )
            
            db = get_db()
            db.update('issue_orders', {'status': 'approved'}, 'issue_id=?', (issue_id,))
            
            logger.info(f"Approved issue {issue_id}")
        except Exception as e:
            logger.error(f"Failed to approve issue: {e}")
            raise
    
    @staticmethod
    def execute_issue(issue_id: str, employee_id: str, user_id: int):
        """
        Execute issue order (actually deduct stock).
        
        Args:
            issue_id: Issue order ID
            employee_id: Employee executing
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Get issue details
                issue = db.fetch_one("SELECT * FROM issue_orders WHERE issue_id=?", (issue_id,))
                if not issue:
                    raise ValidationError(f"Issue {issue_id} not found")
                
                if issue['status'] != 'approved':
                    raise ValidationError("Issue must be approved first")
                
                # Get items
                items = db.fetch_all("SELECT * FROM issue_order_items WHERE issue_id=?", (issue_id,))
                
                # Deduct stock for each item
                for item in items:
                    InventoryManager.deduct_stock(
                        product_id=item['product_id'],
                        quantity=item['quantity'],
                        user_id=user_id
                    )
                
                # Update status
                db.update('issue_orders', {
                    'status': 'executed',
                    'executed_by': employee_id,
                    'executed_at': datetime.now()
                }, 'issue_id=?', (issue_id,))
                
                # Workflow transition
                ApprovalService.approve_document(
                    "ISSUE_ORDER", issue_id, employee_id, "Issue executed"
                )
                
                AuditLogger.log(user_id, 'EXECUTE_ISSUE', 'issue_orders', issue_id)
                logger.info(f"Executed issue {issue_id}")
                
        except Exception as e:
            logger.error(f"Failed to execute issue: {e}")
            raise
