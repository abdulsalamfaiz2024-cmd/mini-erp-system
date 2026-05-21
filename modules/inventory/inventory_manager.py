"""
Inventory Management Module
Handles stock tracking, FIFO costing, and inventory movements.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from core.database import get_db, DatabaseError
from core.logger import get_logger
from modules.security.audit import AuditLogger

logger = get_logger('inventory')

class InventoryManager:
    """Manages Product Inventory"""

    @staticmethod
    def get_stock_level(product_id: str) -> int:
        """Get total available stock for a product"""
        try:
            db = get_db()
            row = db.fetch_one(
                "SELECT SUM(quantity) as total FROM inventory WHERE product_id = ?",
                (product_id,)
            )
            return row['total'] if row and row['total'] else 0
        except Exception as e:
            logger.error(f"Failed to get stock level for {product_id}: {e}")
            return 0

    @staticmethod
    def check_stock_availability(product_id: str, quantity: int) -> bool:
        """Check if enough stock is available"""
        current_stock = InventoryManager.get_stock_level(product_id)
        return current_stock >= quantity

    @staticmethod
    def add_stock(product_id: str, quantity: int, cost_price: float, 
                 warehouse_id: int = 1, batch_number: str = None, 
                 expiry_date: str = None, user_id: int = None):
        """
        Add stock (e.g. from Purchase or Return).
        Implements FIFO by adding a new batch record.
        """
        db = get_db()
        try:
            # Insert new inventory batch
            record_id = db.insert('inventory', {
                'product_id': product_id,
                'warehouse_id': warehouse_id,
                'quantity': quantity,
                'cost_price': cost_price,
                'batch_number': batch_number,
                'expiry_date': expiry_date,
                'received_date': datetime.now().date().isoformat()
            })
            
            # Update product cost price (Weighted Average or Last Price? 
            # Plan says FIFO Costing, which usually applies to consumption.
            # But we might update the 'cost_price' field in products table for reference/current replacement cost).
            # Let's update with latest cost.
            db.update('products', {'cost_price': cost_price}, 'product_id = ?', (product_id,))
            
            AuditLogger.log(user_id, 'ADD_STOCK', 'inventory', str(record_id), new_value=f"+{quantity} @ {cost_price}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add stock for {product_id}: {e}")
            raise

    @staticmethod
    def deduct_stock(product_id: str, quantity: int, user_id: int = None) -> List[Dict]:
        """
        Deduct stock (e.g. for Sale).
        Implements FIFO strategy: consumes oldest batches first.
        Returns list of batches consumed with their cost prices (for profit calculation).
        """
        if quantity <= 0:
            return []

        db = get_db()
        consumed_batches = []
        remaining_qty_to_deduct = quantity
        
        try:
            with db.transaction() as cursor:
                # 1. Get available batches ordered by date (FIFO)
                # We prioritize batches with quantity > 0
                batches = db.fetch_all(
                    """
                    SELECT id, quantity, cost_price, received_date 
                    FROM inventory 
                    WHERE product_id = ? AND quantity > 0 
                    ORDER BY received_date ASC, id ASC
                    """,
                    (product_id,)
                )
                
                total_available = sum(b['quantity'] for b in batches)
                if total_available < quantity:
                    raise ValueError(f"Insufficient stock for {product_id}. Available: {total_available}, Requested: {quantity}")
                
                for batch in batches:
                    if remaining_qty_to_deduct <= 0:
                        break
                        
                    deduct_from_batch = min(batch['quantity'], remaining_qty_to_deduct)
                    
                    # Update batch quantity
                    new_qty = batch['quantity'] - deduct_from_batch
                    db.update('inventory', {'quantity': new_qty}, 'id = ?', (batch['id'],))
                    
                    # Record consumption logic
                    consumed_batches.append({
                        'batch_id': batch['id'],
                        'quantity': deduct_from_batch,
                        'cost_price': batch['cost_price']
                    })
                    
                    remaining_qty_to_deduct -= deduct_from_batch
                    
                AuditLogger.log(user_id, 'DEDUCT_STOCK', 'inventory', product_id, new_value=f"-{quantity}")
                
            return consumed_batches
            
        except Exception as e:
            logger.error(f"Failed to deduct stock for {product_id}: {e}")
            raise

    @staticmethod
    def get_inventory_valuation() -> float:
        """Calculate total value of inventory (FIFO basis)"""
        db = get_db()
        row = db.fetch_one("SELECT SUM(quantity * cost_price) as value FROM inventory")
        return row['value'] if row and row['value'] else 0.0
