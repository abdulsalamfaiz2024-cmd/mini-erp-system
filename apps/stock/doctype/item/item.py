"""
Item Controller
Handles Item lifecycle - auto-creates Bin entries for inventory tracking.
Following ERPNext pattern.
"""
from controllers.transaction_base import TransactionBase
from core.database import db, get_table_name
import core.frappe as frappe


class Item(TransactionBase):
    """
    Item Document Controller.
    Creates Bin entries for stock tracking when Item is saved.
    """
    
    def on_save(self):
        """Called after Item is saved"""
        super().on_save() if hasattr(super(), 'on_save') else None
        self.create_default_bin()
    
    def create_default_bin(self):
        """Create Bin entry for default warehouse if not exists"""
        item_code = self.name
        default_warehouse = self._data.get('default_warehouse') or 'Stores - Main'
        
        if not item_code:
            return
        
        # Check if Bin already exists
        table = get_table_name("Bin")
        existing = db.sql(
            f"SELECT name FROM {table} WHERE item_code = ? AND warehouse = ?",
            (item_code, default_warehouse),
            as_dict=True
        )
        
        if not existing:
            # Create new Bin with zero quantities
            try:
                bin_doc = frappe.get_doc("Bin")
                bin_doc.item_code = item_code
                bin_doc.warehouse = default_warehouse
                bin_doc.actual_qty = 0
                bin_doc.reserved_qty = 0
                bin_doc.ordered_qty = 0
                bin_doc.projected_qty = 0
                bin_doc.save()
                print(f"Created Bin for {item_code} in {default_warehouse}")
            except Exception as e:
                print(f"Could not create Bin: {e}")
    
    def validate(self):
        """Validate Item before saving"""
        super().validate() if hasattr(super(), 'validate') else None
        self.validate_item_code()
        self.validate_stock_uom()
    
    def validate_item_code(self):
        """Ensure item has valid code"""
        if not self._data.get('item_name'):
            raise ValueError("Item Name is required")
    
    def validate_stock_uom(self):
        """Set default UOM if not specified"""
        if not self._data.get('stock_uom'):
            self._data['stock_uom'] = 'Unit'


def get_controller():
    """Return the Item controller class"""
    return Item
