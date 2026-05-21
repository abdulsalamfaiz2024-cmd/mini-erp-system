"""
CRM Module
Handles customer analysis, history, and segmentation.
"""

from typing import List, Dict
from core.database import get_db
from core.logger import get_logger

logger = get_logger('crm')

class CRMManager:
    """Manages Customer Relations"""

    @staticmethod
    def get_customer_history(customer_id: str) -> List[Dict]:
        """Get all orders and payments for a customer"""
        db = get_db()
        history = []
        
        # Get Orders
        orders = db.fetch_all(
            "SELECT * FROM sales_orders WHERE customer_id = ? ORDER BY order_date DESC", 
            (customer_id,)
        )
        for o in orders:
            history.append({
                'type': 'order',
                'date': o['order_date'],
                'reference': o['order_number'],
                'amount': o['total_amount'],
                'status': o['status']
            })
            
        # Get Payments (Need to join or query by entity_id logic)
        # Payments linked to sales_orders which are linked to customer
        # Or if we had customer_id in payments? No.
        # Queries payments for orders of this customer.
        payments = db.fetch_all("""
            SELECT p.* FROM payments p
            JOIN sales_orders so ON p.entity_id = so.order_number
            WHERE p.entity_type = 'sales_order' AND so.customer_id = ?
            ORDER BY p.payment_date DESC
        """, (customer_id,))
        
        for p in payments:
            history.append({
                'type': 'payment',
                'date': p['payment_date'],
                'reference': p['entity_id'], # Order Number
                'amount': p['amount'],
                'status': 'completed'
            })
            
        # Sort by date
        history.sort(key=lambda x: x['date'], reverse=True)
        return history

    @staticmethod
    def get_customer_segmentation() -> List[Dict]:
        """Segment customers based on spending (Gold, Silver, Bronze)"""
        db = get_db()
        # Calculate total spent
        sql = """
            SELECT customer_id, SUM(total_amount) as total_spent, COUNT(*) as order_count 
            FROM sales_orders 
            WHERE status != 'draft' 
            GROUP BY customer_id
        """
        rows = db.fetch_all(sql)
        
        segments = []
        for row in rows:
            spent = row['total_spent']
            segment = 'Bronze'
            if spent > 10000:
                segment = 'Platinum'
            elif spent > 5000:
                segment = 'Gold'
            elif spent > 1000:
                segment = 'Silver'
                
            segments.append({
                'customer_id': row['customer_id'],
                'total_spent': spent,
                'order_count': row['order_count'],
                'segment': segment
            })
            
        return segments

    @staticmethod
    def check_credit_limit(customer_id: str, amount: float) -> bool:
        """Check if new amount exceeds credit limit"""
        db = get_db()
        cust = db.fetch_one("SELECT credit_limit, current_balance FROM customers WHERE customer_id = ?", (customer_id,))
        if not cust:
            return False
            
        limit = cust['credit_limit']
        balance = cust['current_balance']
        
        # If limit is 0, unlimited? Or no credit? Let's assume 0 means NO credit (Cash only).
        # Or default unlimited? Usually 0 means strict.
        if limit == 0:
            return False # Strict
            
        return (balance + amount) <= limit
