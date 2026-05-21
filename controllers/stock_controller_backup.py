"""
Stock Controller
Base class for documents that affect stock (Delivery Notes, Stock Entries).
"""
from controllers.accounts_controller import AccountsController
from core.database import db, get_table_name
import core.frappe as frappe


class StockController(AccountsController):
    """
    Base class for stock-affecting documents.
    Provides:
    - Stock Ledger Entry creation
    - Warehouse validation
    - Bin updates
    """
    
    def validate(self):
        super().validate()
        self.validate_warehouse()
    
    def validate_warehouse(self):
        """Validate that warehouses exist"""
        for item in self.get_items():
            warehouse = item.get('warehouse')
            if warehouse:
                # Check if warehouse exists
                if not db.exists("Warehouse", warehouse):
                    raise ValueError(f"Row {item.get('idx', '?')}: Warehouse {warehouse} does not exist")
    
    def make_sl_entries(self, sl_entries: list, cancel=False):
        """
        Create Stock Ledger Entries.
        sl_entries: list of dicts with item_code, warehouse, actual_qty, etc.
        """
        for sle in sl_entries:
            if cancel:
                sle['actual_qty'] = -sle['actual_qty']
            
            sle_doc = frappe.get_doc("Stock Ledger Entry", **sle)
            sle_doc.voucher_type = self.doctype
            sle_doc.voucher_no = self.name
            sle_doc.posting_date = self._data.get('posting_date') or self._data.get('transaction_date')
            sle_doc.save()
            
            # Update Bin
            self.update_bin(sle)
    
    def update_bin(self, sle: dict):
        """Update Bin (real-time stock quantity)"""
        # Simplified bin update
        table = get_table_name("Bin")
        item_code = sle.get('item_code')
        warehouse = sle.get('warehouse')
        actual_qty = float(sle.get('actual_qty', 0))
        
        # Check if Bin exists
        existing = db.sql(
            f"SELECT name, actual_qty FROM {table} WHERE item_code = ? AND warehouse = ?",
            (item_code, warehouse),
            as_dict=True
        )
        
        if existing:
            new_qty = float(existing[0].get('actual_qty', 0)) + actual_qty
            db.sql(
                f"UPDATE {table} SET actual_qty = ? WHERE name = ?",
                (new_qty, existing[0]['name'])
            )
        else:
            # Create new Bin
            bin_doc = frappe.get_doc("Bin")
            bin_doc.item_code = item_code
            bin_doc.warehouse = warehouse
            bin_doc.actual_qty = actual_qty
            bin_doc.save()
    
    def get_sl_entries(self, item, args: dict) -> dict:
        """Helper to create Stock Ledger Entry dict"""
        sle = {
            "doctype": "Stock Ledger Entry",
            "item_code": item.get('item_code'),
            "warehouse": item.get('warehouse') or self._data.get('set_warehouse'),
            "actual_qty": float(item.get('qty', 0)),
            "valuation_rate": float(item.get('rate', 0)),
        }
        sle.update(args)
        return sle
