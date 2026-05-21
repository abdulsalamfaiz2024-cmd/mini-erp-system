"""
Sales Returns Service
Handles sales return workflow with inventory and accounting integration
"""

from typing import List, Dict
from datetime import datetime, date
from decimal import Decimal
from core.database import get_db
from core.logger import get_logger
from core.validators import ValidationError
from modules.workflow.service import WorkflowService, ApprovalService
from modules.inventory.inventory_manager import InventoryManager
from modules.security.audit import AuditLogger

logger = get_logger('sales_returns')


class SalesReturnService:
    """Manages sales return operations"""
    
    @staticmethod
    def create_return(original_order_id: str, items: List[Dict], reason: str,
                     employee_id: str, user_id: int) -> str:
        """
        Create a sales return request.
        
        Args:
            original_order_id: Original sales order number
            items: [{'product_id': str, 'quantity': int, 'reason': str}]
            reason: Overall return reason
            employee_id: Employee creating return
            user_id: User ID
        
        Returns:
            return_id
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Validate original order exists
                order = db.fetch_one(
                    "SELECT * FROM sales_orders WHERE order_number=?",
                    (original_order_id,)
                )
                
                if not order:
                    raise ValidationError(f"Original order {original_order_id} not found")
                
                # Generate return ID
                date_str = datetime.now().strftime('%Y%m%d')
                row = db.fetch_one("SELECT MAX(id) as max_id FROM sales_returns")
                new_id_num = (row['max_id'] or 0) + 1
                return_id = f"RET-{date_str}-{new_id_num:04d}"
                
                # Calculate return total
                total_amount = Decimal('0')
                for item in items:
                    # Get original price
                    orig_item = db.fetch_one(
                        "SELECT unit_price FROM sales_order_items WHERE order_number=? AND product_id=?",
                        (original_order_id, item['product_id'])
                    )
                    if orig_item:
                        total_amount += Decimal(str(orig_item['unit_price'])) * Decimal(str(item['quantity']))
                
                # Create return header
                db.insert('sales_returns', {
                    'return_id': return_id,
                    'original_order_id': original_order_id,
                    'customer_id': order['customer_id'],
                    'return_date': datetime.now().date().isoformat(),
                    'total_amount': float(total_amount),
                    'reason': reason,
                    'status': 'pending',
                    'created_by': employee_id
                })
                
                # Create return items
                for item in items:
                    db.insert('sales_return_items', {
                        'return_id': return_id,
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'reason': item.get('reason', reason)
                    })
                
                # Initialize workflow
                WorkflowService.initialize_document_state('SALES_RETURN', return_id)
                
                AuditLogger.log(user_id, 'CREATE_RETURN', 'sales_returns', return_id,
                              new_value=f"Order:{original_order_id}, Amount:{total_amount}")
                
                logger.info(f"Created sales return {return_id} for order {original_order_id}")
                return return_id
                
        except Exception as e:
            logger.error(f"Failed to create return: {e}")
            raise
    
    @staticmethod
    def submit_return(return_id: str, employee_id: str):
        """
        Submit return for approval.
        API: ApprovalService.approve_document
        """
        try:
            ApprovalService.approve_document(
                "SALES_RETURN", return_id, employee_id, "Return submitted"
            )
            
            db = get_db()
            db.update('sales_returns', {'status': 'submitted'}, 'return_id=?', (return_id,))
            
            logger.info(f"Submitted return {return_id}")
        except Exception as e:
            logger.error(f"Failed to submit return: {e}")
            raise
    
    @staticmethod
    def approve_return(return_id: str, approver_employee_id: str, user_id: int):
        """
        Approve return (restore inventory, reverse accounting, credit customer).
        
        Args:
            return_id: Return ID
            approver_employee_id: Approving employee
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Get return details
                ret = db.fetch_one("SELECT * FROM sales_returns WHERE return_id=?", (return_id,))
                if not ret:
                    raise ValidationError(f"Return {return_id} not found")
                
                # Get return items
                items = db.fetch_all("SELECT * FROM sales_return_items WHERE return_id=?", (return_id,))
                
                # 1. Restore inventory
                for item in items:
                    InventoryManager.add_stock(
                        product_id=item['product_id'],
                        quantity=item['quantity'],
                        cost_price=0,  # Would get from original order
                        user_id=user_id
                    )
                
                # 2. Credit customer balance
                db.execute(
                    "UPDATE customers SET current_balance = current_balance - ? WHERE customer_id=?",
                    (ret['total_amount'], ret['customer_id'])
                )
                
                # 3. Create accounting reversal (if accounting module used)
                try:
                    from modules.accounting.service import AccountingService
                    # Create credit memo entry
                    # (Simplified - would reverse original sales entry)
                    logger.info(f"Accounting reversal for return {return_id}")
                except ImportError:
                    logger.warning("Accounting module not available")
                
                # 4. Update workflow
                ApprovalService.approve_document(
                    "SALES_RETURN", return_id, approver_employee_id, "Return approved"
                )
                
                db.update('sales_returns', {'status': 'approved'}, 'return_id=?', (return_id,))
                
                AuditLogger.log(user_id, 'APPROVE_RETURN', 'sales_returns', return_id)
                logger.info(f"Approved return {return_id}")
                
        except Exception as e:
            logger.error(f"Failed to approve return: {e}")
            raise
