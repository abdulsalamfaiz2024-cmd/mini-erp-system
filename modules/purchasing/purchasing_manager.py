"""
Purchasing Management Module
Handles procurement: Purchase Orders -> Goods Receipt -> Payment
"""

from datetime import datetime
from typing import List, Dict, Optional
from core.database import get_db
from core.logger import get_logger
from core.validators import ValidationError
from modules.security.audit import AuditLogger
from modules.inventory.inventory_manager import InventoryManager

logger = get_logger('purchasing')

class PurchasingManager:
    """Manages Purchasing Operations"""

    @staticmethod
    def create_purchase_order(supplier_id: str, items: List[Dict], user_id: int, 
                            expected_date: str = None, employee_id: str = None) -> str:
        """
        Create a new purchase order.
        Items: [{'product_id': 'P1', 'quantity': 100, 'unit_price': 50, 'tax_rate': 0, 'discount_amount': 0}]
        """
        db = get_db()
        order_date = datetime.now().date().isoformat()
        
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
        
        try:
            # Generate PO Number
            date_str = datetime.now().strftime('%Y%m%d')
            prefix = f"PO-{date_str}-"
            
            cursor = db.conn.cursor()
            cursor.execute(f"SELECT po_number FROM purchase_orders WHERE po_number LIKE '{prefix}%' ORDER BY po_number DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                last_num = int(row[0].split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            po_number = f"{prefix}{new_num:04d}"
            
            with db.transaction() as cursor:
                db.insert('purchase_orders', {
                    'po_number': po_number,
                    'supplier_id': supplier_id,
                    'order_date': order_date,
                    'expected_delivery_date': expected_date,
                    'status': 'draft',
                    'subtotal': subtotal,
                    'total_tax': total_tax,
                    'total_discount': total_discount,
                    'total_amount': gra_total,
                    'total_amount': gra_total,
                    'employee_id': employee_id,
                    'created_by': user_id
                }, return_id=False)
                
                for i, item in enumerate(processed_items):
                    db.insert('purchase_order_items', {
                        'po_number': po_number,
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price'],
                        'tax_rate': item['tax_rate'],
                        'tax_amount': item['tax_amount'],
                        'discount_amount': item['discount_amount'],
                        'total_price': item['total_price'],
                        'line_number': i + 1
                    })
                    
                AuditLogger.log(user_id, 'CREATE_PO', 'purchase_orders', po_number, new_value=gra_total)
                
            return po_number
            
        except Exception as e:
            logger.error(f"Failed to create PO: {e}", exc_info=True)
            raise

    @staticmethod
    def receive_items(po_number: str, received_items: List[Dict], user_id: int, warehouse_id: int = 1):
        """
        Receive items against a PO.
        received_items: [{'product_id': 'P1', 'quantity': 50, 'expiry_date': '2026-01-01'}]
        """
        db = get_db()
        try:
            with db.transaction() as cursor:
                po = db.fetch_one("SELECT * FROM purchase_orders WHERE po_number = ?", (po_number,))
                if not po:
                    raise ValidationError(f"PO {po_number} not found")
                
                # Update Inventory and PO Items
                for item in received_items:
                    prod_id = item['product_id']
                    qty = item['quantity']
                    expiry = item.get('expiry_date')
                    
                    if qty <= 0: continue

                    # Find PO Item to get cost price
                    po_item = db.fetch_one(
                        "SELECT * FROM purchase_order_items WHERE po_number = ? AND product_id = ?",
                        (po_number, prod_id)
                    )
                    
                    if not po_item:
                         logger.warning(f"Received product {prod_id} not in PO {po_number}")
                         cost_price = 0 # Or fetch from product master
                    else:
                         cost_price = po_item['unit_price']
                         
                         # Update received quantity in PO Item
                         new_received = (po_item['received_quantity'] or 0) + qty
                         db.update('purchase_order_items', {'received_quantity': new_received}, 'id = ?', (po_item['id'],))

                    # Add to Inventory
                    batch_num = f"BATCH-{po_number}-{prod_id}"
                    InventoryManager.add_stock(prod_id, qty, cost_price, warehouse_id, 
                                             batch_number=batch_num, expiry_date=expiry, user_id=user_id)
                
                # Check execution status
                # If all items received fully, mark PO as 'received' or 'completed'
                # For now, just set to 'partial' or keep 'approved'. 
                # Let's verify completeness:
                all_items = db.fetch_all("SELECT * FROM purchase_order_items WHERE po_number = ?", (po_number,))
                fully_received = all(i['received_quantity'] >= i['quantity'] for i in all_items)
                
                new_status = 'received' if fully_received else 'partial_received'
                db.update('purchase_orders', {'status': new_status}, 'po_number = ?', (po_number,))
                
                # Update Supplier Balance (Need to pay them)
                # PO amount is a liability.
                # Assuming "status='received'" implies liability recognized? 
                # Or liability recognized on Invoice/Bill? 
                # Mini-ERP: recognize on Receipt for simplicity, or separate Bill step.
                # Let's say liability is tracked via 'unpaid' POs.
                
                # Update Supplier 'current_balance' (Amount we owe them - Credit)
                # Actually, suppliers table usually tracks what we owe.
                # Increase balance (liability)
                # Calculate value of received goods
                received_value = sum(item['quantity'] * 
                                   (db.fetch_one("SELECT unit_price FROM purchase_order_items WHERE po_number=? AND product_id=?", 
                                               (po_number, item['product_id']))['unit_price'])
                                   for item in received_items)
                                   
                supp = db.fetch_one("SELECT current_balance FROM suppliers WHERE supplier_id = ?", (po['supplier_id'],))
                new_balance = (supp['current_balance'] or 0) + received_value
                db.update('suppliers', {'current_balance': new_balance}, 'supplier_id = ?', (po['supplier_id'],))
                
                AuditLogger.log(user_id, 'RECEIVE_ITEMS', 'purchase_orders', po_number, new_value=new_status)

        except Exception as e:
             logger.error(f"Failed to receive items for {po_number}: {e}", exc_info=True)
             raise

    @staticmethod
    def record_payment(po_number: str, amount: float, payment_method: str, user_id: int):
        """Pay a supplier for a PO"""
        db = get_db()
        try:
            with db.transaction() as cursor:
                po = db.fetch_one("SELECT * FROM purchase_orders WHERE po_number = ?", (po_number,))
                if not po:
                    raise ValidationError(f"PO {po_number} not found")
                    
                new_paid = (po['paid_amount'] or 0) + amount
                new_remaining = po['total_amount'] - new_paid
                
                # Record PaymentOut
                db.insert('payments', {
                    'payment_type': 'expense', # or "payment_out"
                    'entity_type': 'purchase_order',
                    'entity_id': po_number,
                    'amount': amount,
                    'payment_date': datetime.now().date().isoformat(),
                    'payment_method': payment_method,
                    'created_by': user_id
                })
                
                db.update('purchase_orders', {
                    'paid_amount': new_paid, 
                    'remaining_amount': new_remaining
                }, 'po_number = ?', (po_number,))
                
                # Decrease Supplier Balance (We paid them, so liability decreases)
                supp = db.fetch_one("SELECT current_balance FROM suppliers WHERE supplier_id = ?", (po['supplier_id'],))
                new_balance = supp['current_balance'] - amount
                db.update('suppliers', {'current_balance': new_balance}, 'supplier_id = ?', (po['supplier_id'],))
                
                AuditLogger.log(user_id, 'PAY_SUPPLIER', 'purchase_orders', po_number, new_value=f"{amount}")

        except Exception as e:
            logger.error(f"Failed to record payment for PO {po_number}: {e}", exc_info=True)
            raise
