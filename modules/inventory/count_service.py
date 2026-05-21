"""
Inventory Count Service (Stocktaking)
Handles physical inventory counts with adjustment workflow
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

logger = get_logger('inventory_count')


class InventoryCountService:
    """Manages inventory count (stocktaking) operations"""
    
    @staticmethod
    def start_count(count_date: date, warehouse_id: int, employee_id: str,
                   user_id: int) -> str:
        """
        Start an inventory count (snapshot current inventory).
        
        Args:
            count_date: Count date
            warehouse_id: Warehouse being counted
            employee_id: Employee starting count
            user_id: User ID
        
        Returns:
            count_id
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Generate count ID
                date_str = count_date.strftime('%Y%m%d')
                row = db.fetch_one("SELECT MAX(id) as max_id FROM inventory_counts")
                new_id_num = (row['max_id'] or 0) + 1
                count_id = f"CNT-{date_str}-{new_id_num:04d}"
                
                # Create count header
                db.insert('inventory_counts', {
                    'count_id': count_id,
                    'count_date': count_date.isoformat(),
                    'warehouse_id': warehouse_id,
                    'status': 'in_progress',
                    'started_by': employee_id,
                    'started_at': datetime.now()
                })
                
                # Snapshot current inventory
                inventory = db.fetch_all(
                    "SELECT product_id, SUM(quantity) as system_qty FROM inventory WHERE warehouse_id=? GROUP BY product_id",
                    (warehouse_id,)
                )
                
                for item in inventory:
                    db.insert('inventory_count_lines', {
                        'count_id': count_id,
                        'product_id': item['product_id'],
                        'system_quantity': item['system_qty'],
                        'counted_quantity': None,  # To be filled
                        'variance': 0
                    })
                
                # Initialize workflow
                WorkflowService.initialize_document_state('INVENTORY_COUNT', count_id)
                
                AuditLogger.log(user_id, 'START_COUNT', 'inventory_counts', count_id)
                logger.info(f"Started inventory count {count_id}")
                return count_id
                
        except Exception as e:
            logger.error(f"Failed to start count: {e}")
            raise
    
    @staticmethod
    def submit_count(count_id: str, counts: List[Dict], employee_id: str, user_id: int):
        """
        Submit counted quantities and calculate variances.
        
        Args:
            count_id: Count ID
            counts: [{'product_id': str, 'counted_quantity': int}]
            employee_id: Employee submitting
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                for count in counts:
                    # Get system quantity
                    line = db.fetch_one(
                        "SELECT system_quantity FROM inventory_count_lines WHERE count_id=? AND product_id=?",
                        (count_id, count['product_id'])
                    )
                    
                    if line:
                        system_qty = line['system_quantity']
                        counted_qty = count['counted_quantity']
                        variance = counted_qty - system_qty
                        
                        db.update('inventory_count_lines', {
                            'counted_quantity': counted_qty,
                            'variance': variance
                        }, 'count_id=? AND product_id=?', (count_id, count['product_id']))
                
                # Update count status
                db.update('inventory_counts', {
                    'status': 'submitted',
                    'submitted_by': employee_id,
                    'submitted_at': datetime.now()
                }, 'count_id=?', (count_id,))
                
                # Workflow transition
                ApprovalService.approve_document(
                    "INVENTORY_COUNT", count_id, employee_id, "Count submitted"
                )
                
                AuditLogger.log(user_id, 'SUBMIT_COUNT', 'inventory_counts', count_id)
                logger.info(f"Submitted count {count_id}")
                
        except Exception as e:
            logger.error(f"Failed to submit count: {e}")
            raise
    
    @staticmethod
    def approve_adjustment(count_id: str, approver_employee_id: str, user_id: int):
        """
        Approve inventory adjustment (update quantities and create accounting entries).
        
        Args:
            count_id: Count ID
            approver_employee_id: Approving employee
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Get count lines with variances
                variances = db.fetch_all(
                    "SELECT * FROM inventory_count_lines WHERE count_id=? AND variance != 0",
                    (count_id,)
                )
                
                total_value_diff = Decimal('0')
                
                for var in variances:
                    # Adjust inventory
                    if var['variance'] > 0:
                        # Increase
                        InventoryManager.add_stock(
                            product_id=var['product_id'],
                            quantity=var['variance'],
                            cost_price=0,  # Would get average cost
                            user_id=user_id
                        )
                    else:
                        # Decrease
                        InventoryManager.deduct_stock(
                            product_id=var['product_id'],
                            quantity=abs(var['variance']),
                            user_id=user_id
                        )
                    
                    # Calculate value impact
                    product = db.fetch_one("SELECT cost_price FROM products WHERE product_id=?", (var['product_id'],))
                    if product:
                        value_diff = Decimal(str(product['cost_price'])) * Decimal(str(var['variance']))
                        total_value_diff += value_diff
                
                # Create accounting entry for variance
                if total_value_diff != 0:
                    try:
                        from modules.accounting.service import AccountingService
                        # Create inventory variance entry
                        # Dr/Cr Inventory, Cr/Dr Inventory Variance Expense
                        lines = []
                        if total_value_diff > 0:
                            # Overage
                            lines = [
                                {'account_id': '1030', 'debit': float(total_value_diff), 'credit': 0, 'description': f'Count overage {count_id}'},
                                {'account_id': '6010', 'debit': 0, 'credit': float(total_value_diff), 'description': f'Variance income {count_id}'}
                            ]
                        else:
                            # Shortage
                            lines = [
                                {'account_id': '6010', 'debit': float(abs(total_value_diff)), 'credit': 0, 'description': f'Variance expense {count_id}'},
                                {'account_id': '1030', 'debit': 0, 'credit': float(abs(total_value_diff)), 'description': f'Count shortage {count_id}'}
                            ]
                        
                        journal_id = AccountingService.create_journal_entry(
                            entry_date=datetime.now().date(),
                            description=f"Inventory Count Adjustment {count_id}",
                            lines=lines,
                            reference=count_id,
                            user_id=user_id
                        )
                        AccountingService.post_journal(journal_id, user_id)
                        logger.info(f"Created accounting entry {journal_id} for count {count_id}")
                    except ImportError:
                        logger.warning("Accounting module not available")
                
                # Update workflow
                ApprovalService.approve_document(
                    "INVENTORY_COUNT", count_id, approver_employee_id, "Adjustment approved"
                )
                
                db.update('inventory_counts', {
                    'status': 'approved',
                    'approved_by': approver_employee_id,
                    'approved_at': datetime.now()
                }, 'count_id=?', (count_id,))
                
                AuditLogger.log(user_id, 'APPROVE_COUNT', 'inventory_counts', count_id,
                              new_value=f"Variance: ${total_value_diff}")
                logger.info(f"Approved count adjustment {count_id}")
                
        except Exception as e:
            logger.error(f"Failed to approve count: {e}")
            raise
