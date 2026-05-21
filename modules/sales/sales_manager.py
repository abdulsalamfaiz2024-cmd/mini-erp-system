"""
Sales Management Module
Handles the complete sales lifecycle: Quotation -> Order -> Invoice -> Payment
"""

from datetime import datetime
from typing import List, Dict, Optional
from core.database import get_db, DatabaseError
from core.logger import get_logger
from core.validators import BusinessValidator, ValidationError
from modules.security.audit import AuditLogger
from modules.inventory.inventory_manager import InventoryManager

logger = get_logger('sales')

class SalesManager:
    """Manages Sales Operations"""

    @staticmethod
    def create_order(customer_id: str, items: List[Dict], user_id: int, 
                    order_date: str = None, status: str = 'draft', employee_id: str = None) -> str:
        """
        Create a new sales order / invoice.
        Items list: [{'product_id': 'P1', 'quantity': 10, 'unit_price': 100, 'tax_rate': 0, 'discount_amount': 0}]
        """
        db = get_db()
        order_date = order_date or datetime.now().date().isoformat()
        
        # Calculate Totals
        subtotal = 0.0
        total_tax = 0.0
        total_discount = 0.0
        gra_total = 0.0
        
        processed_items = []
        
        for item in items:
            qty = item['quantity']
            price = item['unit_price']
            tax_rate = item.get('tax_rate', 0.0)
            disc = item.get('discount_amount', 0.0)
            
            gross = qty * price
            # specific logic: discount is usually per line total? or per unit? 
            # Assuming discount_amount is TOTAL discount for this line.
            
            taxable_amount = gross - disc
            tax_amt = taxable_amount * (tax_rate / 100.0)
            line_total = taxable_amount + tax_amt
            
            subtotal += gross
            total_discount += disc
            total_tax += tax_amt
            gra_total += line_total
            
            processed_items.append({
                'product_id': item['product_id'],
                'quantity': qty,
                'unit_price': price,
                'tax_rate': tax_rate,
                'tax_amount': tax_amt,
                'discount_amount': disc,
                'total_price': line_total
            })
        
        # Generate Order Number
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            prefix = f"SO-{date_str}-"
            
            cursor = db.conn.cursor()
            cursor.execute(f"SELECT order_number FROM sales_orders WHERE order_number LIKE '{prefix}%' ORDER BY order_number DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                last_num = int(row[0].split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
                
            order_number = f"{prefix}{new_num:04d}"
            
            with db.transaction() as cursor:
                # Create Order
                db.insert('sales_orders', {
                    'order_number': order_number,
                    'customer_id': customer_id,
                    'order_date': order_date,
                    'status': status,
                    'subtotal': subtotal,
                    'total_tax': total_tax,
                    'total_discount': total_discount,
                    'total_amount': gra_total,
                    'total_discount': total_discount,
                    'total_amount': gra_total,
                    'employee_id': employee_id,
                    'created_by': user_id
                }, return_id=False)
                
                
                # Create Order Items
                for i, item in enumerate(processed_items):
                    db.insert('sales_order_items', {
                        'order_number': order_number,
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price'],
                        'tax_rate': item['tax_rate'],
                        'tax_amount': item['tax_amount'],
                        'discount_amount': item['discount_amount'],
                        'total_price': item['total_price'],
                        'line_number': i + 1
                    })
                
                # INTEGRATION GUARD: Initialize Workflow
                from modules.workflow.service import WorkflowService, WorkflowError
                try:
                    WorkflowService.initialize_document_state('SALES_ORDER', order_number)
                except WorkflowError as e:
                     # Hard Block: Cannot create order without workflow
                     raise ValidationError(f"Workflow Authorization Failed: {e}")

                AuditLogger.log(user_id, 'CREATE_ORDER', 'sales_orders', order_number, new_value=gra_total)
                
            return order_number
            
        except Exception as e:
            logger.error(f"Failed to create order: {e}", exc_info=True)
            raise

    @staticmethod
    def generate_invoice(order_number: str, user_id: int) -> bool:
        """
        Convert Order to Invoice status and deduct stock.
        """
        db = get_db()
        try:
            # INTEGRATION GUARD: Verify Workflow State
            from modules.workflow.service import WorkflowService
            state = WorkflowService.get_current_state('SALES_ORDER', order_number)
            if not state:
                 raise ValidationError("Security Violation: Order not tracked by Workflow Engine")
            
            # Stricter Check for Remediation
            # Only allow invoicing if state is strictly 'Completed' or 'Approved' (if that's final)
            allowed_states = ['Completed', 'Approved'] 
            if state['name'] not in allowed_states:
                 raise ValidationError(f"Order cannot be invoiced in state: {state['name']} (Must be {allowed_states})")

            with db.transaction() as cursor:
                # Get Order
                order = db.fetch_one("SELECT * FROM sales_orders WHERE order_number = ?", (order_number,))
                if not order:
                    raise ValidationError(f"Order {order_number} not found")
                    
                if order['status'] == 'invoiced':
                     raise ValidationError(f"Order {order_number} already invoiced")

                # Get Items
                items = db.fetch_all("SELECT * FROM sales_order_items WHERE order_number = ?", (order_number,))
                
                total_cost = 0.0
                total_profit = 0.0
                
                # Check Stock first
                for item in items:
                    if not InventoryManager.check_stock_availability(item['product_id'], item['quantity']):
                        raise ValidationError(f"Insufficient stock for {item['product_id']}")

                # Deduct Stock and Calculate Profit
                for item in items:
                    consumed_batches = InventoryManager.deduct_stock(item['product_id'], item['quantity'], user_id)
                    
                    # Calculate item cost from consumed batches
                    item_cost = sum(b['quantity'] * b['cost_price'] for b in consumed_batches)
                    item_profit = item['total_price'] - item_cost
                    
                    # Update Item with cost/profit
                    db.update('sales_order_items', 
                             {'cost_price': item_cost, 'profit': item_profit}, 
                             'id = ?', (item['id'],))
                             
                    total_cost += item_cost
                    total_profit += item_profit
                
                # Update Order Status and Financials
                db.update('sales_orders', {
                    'status': 'invoiced',
                    'total_cost': total_cost,
                    'total_profit': total_profit
                }, 'order_number = ?', (order_number,))
                
                # Update Customer Balance
                # Get current balance
                cust = db.fetch_one("SELECT current_balance FROM customers WHERE customer_id = ?", (order['customer_id'],))
                new_balance = (cust['current_balance'] or 0) + order['total_amount']
                
                db.update('customers', {'current_balance': new_balance}, 'customer_id = ?', (order['customer_id'],))
                
                AuditLogger.log(user_id, 'GENERATE_INVOICE', 'sales_orders', order_number, new_value='invoiced')
                return True

        except Exception as e:
            logger.error(f"Failed to generate invoice for {order_number}: {e}", exc_info=True)
            raise

    @staticmethod
    def record_payment(order_number: str, amount: float, payment_method: str, user_id: int):
        """
        Record a payment against an invoice.
        """
        db = get_db()
        try:
            with db.transaction() as cursor:
                # Get Order
                order = db.fetch_one("SELECT * FROM sales_orders WHERE order_number = ?", (order_number,))
                if not order:
                    raise ValidationError(f"Order {order_number} not found")
                
                # INTEGRATION GUARD: Payment only allowed on Invoiced orders
                if order['status'] != 'invoiced':
                     raise ValidationError(f"Cannot record payment on non-invoiced order (Status: {order['status']})")
                
                new_paid_amount = order['paid_amount'] + amount
                if new_paid_amount > order['total_amount']:
                    raise ValidationError(f"Payment amount exceeds total (Remaining: {order['total_amount'] - order['paid_amount']})")
                
                new_remaining = order['total_amount'] - new_paid_amount
                payment_status = 'paid' if new_remaining == 0 else 'partial'
                
                # Create Payment Record
                db.insert('payments', {
                    'payment_type': 'income',
                    'entity_type': 'sales_order',
                    'entity_id': order_number,
                    'amount': amount,
                    'payment_date': datetime.now().date().isoformat(),
                    'payment_method': payment_method,
                    'created_by': user_id
                })
                
                # Update Order
                db.update('sales_orders', {
                    'paid_amount': new_paid_amount,
                    'remaining_amount': new_remaining,
                    'payment_status': payment_status
                }, 'order_number = ?', (order_number,))
                
                # Update Customer Balance (decrease by payment)
                cust = db.fetch_one("SELECT current_balance FROM customers WHERE customer_id = ?", (order['customer_id'],))
                new_balance = cust['current_balance'] - amount
                db.update('customers', {'current_balance': new_balance}, 'customer_id = ?', (order['customer_id'],))
                
                AuditLogger.log(user_id, 'PAYMENT', 'sales_orders', order_number, new_value=f"+{amount}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to record payment for {order_number}: {e}", exc_info=True)
            raise
