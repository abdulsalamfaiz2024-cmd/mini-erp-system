"""
Buying Controller
Base class for buying documents (Purchase Order, Purchase Receipt, Purchase Invoice).
"""
from controllers.stock_controller import StockController
from core.database import db
import core.frappe as frappe


class BuyingController(StockController):
    """
    Base class for buying documents.
    Provides:
    - Supplier validation
    - Purchase pricing logic
    """
    
    def validate(self):
        super().validate()
        self.validate_supplier()
    
    def validate_supplier(self):
        """Validate supplier exists"""
        supplier = self._data.get('supplier')
        if not supplier:
            raise ValueError("Supplier is required")
        
        if not db.exists("Supplier", supplier):
            raise ValueError(f"Supplier {supplier} does not exist")
    
    def set_missing_values(self):
        """Set missing values from supplier/item defaults"""
        supplier = self._data.get('supplier')
        if supplier:
            supplier_name = db.get_value("Supplier", {"name": supplier}, "supplier_name")
            if supplier_name:
                self._data['supplier_name'] = supplier_name
