from typing import List, Dict, Optional
from core.database import get_db, DatabaseError
from modules.sales.models import SalesOrder, SalesOrderItem
from modules.workflow.service import WorkflowService, ApprovalService, WorkflowError
from modules.sales.sales_manager import SalesManager
from core.validators import ValidationError
from datetime import datetime

class SalesOrderService:
    @staticmethod
    def create_order(customer_id: str, items: List[Dict], employee_id: str, user_id: int) -> str:
        """
        Creates a new Sales Order and initializes it in DRAFT state.
        Args:
            items: [{'product_id': 'P1', 'quantity': 1, 'unit_price': 100}]
        """
        # 1. Use SalesManager for persistence (reusing logic for numbering/calculations)
        # SalesManager.create_order calls WorkflowService.initialize_document_state now (since Remediation)
        # So we just delegate.
        try:
            order_id = SalesManager.create_order(
                customer_id=customer_id,
                items=items,
                user_id=user_id,
                employee_id=employee_id,
                status='Draft' # Initial status
            )
            return order_id
        except Exception as e:
            raise ValidationError(f"Failed to create sales order: {e}")

    @staticmethod
    def submit_order(order_id: str, employee_id: str):
        """
        Moves order from DRAFT to SUBMITTED.
        Triggered by Employee who created it (or any active user?).
        """
        # Current State: Draft. Transition -> Submitted.
        # Workflow Definitions: Draft (10) -> Submitted (20).
        # Requires Approval? Draft doesn't. Submitted Does.
        # So this is an "Approve" action on the Draft state?
        # Draft state has requires_approval=False.
        # So calling ApprovalService.approve_document on 'Draft' moves it to 'Submitted'.
        try:
            ApprovalService.approve_document(
                document_type="SALES_ORDER", 
                document_id=order_id, 
                employee_id=employee_id, 
                comment="Submitting Order"
            )
            # Sync Legacy Status
            db = get_db()
            db.execute("UPDATE sales_orders SET status='submitted' WHERE order_number=?", (order_id,))
        except Exception as e:
            raise ValidationError(f"Submission failed: {e}")

    @staticmethod
    def approve_finance(order_id: str, finance_employee_id: str, comment: str = "Finance Approved"):
        """
        Moves order from SUBMITTED to FINANCE_APPROVED.
        Requires Finance Level (3).
        """
        try:
            ApprovalService.approve_document(
                "SALES_ORDER", order_id, finance_employee_id, comment
            )
            # Sync Legacy Status
            db = get_db()
            db.execute("UPDATE sales_orders SET status='approved' WHERE order_number=?", (order_id,))
        except Exception as e:
            raise ValidationError(f"Finance approval failed: {e}")

    @staticmethod
    def release_to_warehouse(order_id: str, employee_id: str, comment: str = "Released to Warehouse"):
        """
        Moves FINANCE_APPROVED -> READY_FOR_WAREHOUSE.
        """
        try:
            ApprovalService.approve_document(
                "SALES_ORDER", order_id, employee_id, comment
            )
            # Sync Legacy Status
            db = get_db()
            db.execute("UPDATE sales_orders SET status='approved' WHERE order_number=?", (order_id,))
        except Exception as e:
            raise ValidationError(f"Warehouse release failed: {e}")
            
    @staticmethod
    def fulfill_order(order_id: str, warehouse_employee_id: str):
        """
        Moves READY_FOR_WAREHOUSE -> COMPLETED.
        Requires Warehouse Level (2).
        """
        try:
            if order_id: # Context check
                 # Auto-Forward: If Finance_Approved, move to Ready_For_Warehouse first
                 state = WorkflowService.get_current_state("SALES_ORDER", order_id)
                 if state and state['name'] == 'Finance_Approved':
                     # Perform intermediate step
                     ApprovalService.approve_document(
                        "SALES_ORDER", order_id, warehouse_employee_id, "Auto-Release to Warehouse"
                     )
            
            ApprovalService.approve_document(
                "SALES_ORDER", order_id, warehouse_employee_id, "Order Fulfilled"
            )
            # Sync Legacy Status
            db = get_db()
            db.execute("UPDATE sales_orders SET status='completed' WHERE order_number=?", (order_id,))
        except Exception as e:
            raise ValidationError(f"Fulfillment failed: {e}")

    @staticmethod
    def reject_order(order_id: str, employee_id: str, reason: str):
        """
        Rejects order to REJECTED state.
        """
        try:
            ApprovalService.reject_document(
                "SALES_ORDER", order_id, employee_id, reason
            )
            # Sync Legacy Status
            db = get_db()
            db.execute("UPDATE sales_orders SET status='rejected' WHERE order_number=?", (order_id,))
        except Exception as e:
            raise ValidationError(f"Rejection failed: {e}")

    @staticmethod
    def get_order(order_id: str) -> Dict:
        """
        Get Order details including Current Workflow State.
        """
        db = get_db()
        order = db.fetch_one("SELECT * FROM sales_orders WHERE order_number = ?", (order_id,))
        if not order:
            return None
            
        state = WorkflowService.get_current_state("SALES_ORDER", order_id)
        
        # Merge info
        return {
            **dict(order),
            'current_state': state['name'] if state else 'Unknown',
            'state_details': state
        }
