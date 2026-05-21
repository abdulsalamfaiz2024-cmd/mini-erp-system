from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

@dataclass
class SalesOrderItem:
    item_id: Optional[int]
    order_id: str
    product_id: str
    quantity: int
    unit_price: float
    total_price: float
    tax_amount: float = 0.0
    discount_amount: float = 0.0

@dataclass
class SalesOrder:
    order_id: str
    customer_id: str
    created_by_employee_id: Optional[str]
    order_date: datetime
    # status is derived, not stored here usually, but keeping field for legacy compat
    status: str 
    total_amount: float
    items: List[SalesOrderItem] = None
    
    @property
    def current_state(self):
        """Helper to get state from service needed"""
        pass
