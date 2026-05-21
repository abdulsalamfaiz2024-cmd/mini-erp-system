"""
Expense Service with Approval Workflow
Extends FinanceManager with workflow-enabled expense approval
"""

from typing import Dict
from datetime import datetime, date
from core.database import get_db
from core.logger import get_logger
from core.validators import ValidationError
from modules.workflow.service import WorkflowService, ApprovalService
from modules.finance.finance_manager import FinanceManager
from modules.security.audit import AuditLogger

logger = get_logger('expense_service')


class ExpenseService:
    """Manages expense approval workflow"""
    
    @staticmethod
    def record_expense(expense_type: str, category: str, amount: float,
                      description: str, employee_id: str, user_id: int,
                     payment_method: str = 'pending') -> str:
        """
        Record an expense (requires approval workflow).
        
        Args:
            expense_type: 'fixed' or 'variable'
            category: Expense category
            amount: Amount
            description: Description
            employee_id: Employee requesting
            user_id: User ID
            payment_method: Payment method (or 'pending')
        
        Returns:
            expense_id
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Use FinanceManager to create expense (unposted)
                expense_id = FinanceManager.add_expense(
                    type=expense_type,
                    category=category,
                    amount=amount,
                    description=description,
                    user_id=user_id,
                    payment_method='pending',  # Not paid yet
                    employee_id=employee_id
                )
                
                # Mark as requiring approval
                db.update('expenses', {
                    'status': 'pending_approval'
                }, 'expense_id=?', (expense_id,))
                
                # Initialize workflow
                WorkflowService.initialize_document_state('EXPENSE', expense_id)
                
                AuditLogger.log(user_id, 'RECORD_EXPENSE', 'expenses', expense_id,
                              new_value=f"${amount}")
                
                logger.info(f"Recorded expense {expense_id}")
                return expense_id
                
        except Exception as e:
            logger.error(f"Failed to record expense: {e}")
            raise
    
    @staticmethod
    def approve_expense(expense_id: str, approver_employee_id: str, user_id: int):
        """
        Approve expense and post to accounting.
        
        Args:
            expense_id: Expense ID
            approver_employee_id: Approving employee
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Get expense
                expense = db.fetch_one("SELECT * FROM expenses WHERE expense_id=?", (expense_id,))
                if not expense:
                    raise ValidationError(f"Expense {expense_id} not found")
                
                # Workflow approval
                ApprovalService.approve_document(
                    "EXPENSE", expense_id, approver_employee_id, "Expense approved"
                )
                
                # Update status
                db.update('expenses', {
                    'status': 'approved',
                    'approved_by': approver_employee_id,
                    'approved_at': datetime.now()
                }, 'expense_id=?', (expense_id,))
                
                # Create accounting entry
                try:
                    from modules.accounting.service import AccountingService
                    lines = [
                        {'account_id': '6010', 'debit': expense['amount'], 'credit': 0, 'description': expense['description']},  # Expense
                        {'account_id': '1010', 'debit': 0, 'credit': expense['amount'], 'description': 'Cash payment'}  # Cash
                    ]
                    journal_id = AccountingService.create_journal_entry(
                        entry_date=datetime.now().date(),
                        description=f"Expense: {expense['description']}",
                        lines=lines,
                        reference=expense_id,
                        user_id=user_id
                    )
                    AccountingService.post_journal(journal_id, user_id)
                    logger.info(f"Created expense entry {journal_id}")
                except ImportError:
                    logger.warning("Accounting module not available")
                
                AuditLogger.log(user_id, 'APPROVE_EXPENSE', 'expenses', expense_id)
                logger.info(f"Approved expense {expense_id}")
                
        except Exception as e:
            logger.error(f"Failed to approve expense: {e}")
            raise
