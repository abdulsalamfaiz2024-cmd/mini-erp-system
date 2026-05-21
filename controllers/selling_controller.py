"""
Selling Controller
Base class for selling documents (Sales Order, Quotation, Delivery Note, Sales Invoice).
"""
from controllers.stock_controller import StockController
from core.database import db
import core.frappe as frappe


class SellingController(StockController):
    """
    Base class for selling documents.
    Provides:
    - Customer validation
    - Credit limit check
    - Pricing logic
    - Commission calculation
    """
    
    def validate(self):
        super().validate()
        self.validate_customer()
        self.validate_selling_price()
        self.set_missing_values()
    
    def validate_customer(self):
        """Validate customer exists"""
        customer = self._data.get('customer')
        if not customer:
            raise ValueError("Customer is required")
        
        if not db.exists("Customer", customer):
            raise ValueError(f"Customer {customer} does not exist")
    
    def validate_selling_price(self):
        """Validate selling price is not below minimum (if configured)"""
        # Simplified - in real ERPNext this checks against Item's min selling rate
        for item in self.get_items():
            rate = float(item.get('rate', 0) or 0)
            if rate <= 0:
                raise ValueError(f"Row {item.get('idx', '?')}: Rate must be greater than 0")
    
    def set_missing_values(self):
        """Set missing values from customer/item defaults"""
        customer = self._data.get('customer')
        if customer:
            # Get customer name
            customer_name = db.get_value("Customer", {"name": customer}, "customer_name")
            if customer_name:
                self._data['customer_name'] = customer_name
        
        # Set item names and rates from Item master
        for item in self.get_items():
            item_code = item.get('item_code')
            if item_code:
                item_data = db.sql(
                    f"SELECT item_name, standard_rate FROM {db.get_table_name('Item') if hasattr(db, 'get_table_name') else 'tabitem'} WHERE item_code = ? OR name = ?",
                    (item_code, item_code),
                    as_dict=True
                )
                if item_data:
                    if not item.get('item_name'):
                        item['item_name'] = item_data[0].get('item_name')
                    if not item.get('rate'):
                        item['rate'] = item_data[0].get('standard_rate', 0)
    
    def check_credit_limit(self):
        """Check if customer has exceeded credit limit"""
        # Simplified implementation
        customer = self._data.get('customer')
        if not customer:
            return
        
        # Get customer's credit limit
        credit_limit = db.get_value("Customer", {"name": customer}, "credit_limit") or 0
        
        if credit_limit > 0:
            # Get outstanding amount (sum of unpaid invoices)
            # This would require Sales Invoice to be implemented
            pass
    
    def get_party_details(self):
        """Get customer details"""
        customer = self._data.get('customer')
        if customer:
            return db.sql(
                f"SELECT * FROM tabcustomer WHERE name = ?",
                (customer,),
                as_dict=True
            )
        return []
    
    def on_submit(self):
        """Called when document is submitted"""
        super().on_submit() if hasattr(super(), 'on_submit') else None
        self.update_customer_balance()
    
    def on_cancel(self):
        """Called when document is cancelled"""
        super().on_cancel() if hasattr(super(), 'on_cancel') else None
        self.update_customer_balance(cancel=True)
    
    def update_customer_balance(self, cancel=False):
        """Update customer outstanding balance - like ERPNext"""
        customer = self._data.get('customer')
        if not customer:
            return
        
        grand_total = float(self._data.get('grand_total', 0) or 0)
        
        if cancel:
            grand_total = -grand_total
        
        # Update customer balance
        try:
            result = db.sql(
                "SELECT current_balance FROM customers WHERE customer_id = ? OR name = ?",
                (customer, customer),
                as_dict=True
            )
            
            if result:
                current = float(result[0].get('current_balance', 0) or 0)
                new_balance = current + grand_total
                
                db.sql(
                    "UPDATE customers SET current_balance = ? WHERE customer_id = ? OR name = ?",
                    (new_balance, customer, customer)
                )
                db.commit()
                print(f"Customer {customer} balance: {current} -> {new_balance}")
        except Exception as e:
            print(f"Could not update customer balance: {e}")
    
    def update_reserved_stock(self):
        """Update reserved qty in Bin when order submitted"""
        from core.database import get_table_name
        
        for item in self.get_items():
            item_code = item.get('item_code')
            qty = float(item.get('qty', 0))
            warehouse = item.get('warehouse') or self._data.get('set_warehouse') or 'Stores - Main'
            
            # Update Bin reserved_qty
            table = get_table_name("Bin")
            existing = db.sql(
                f"SELECT name, reserved_qty, actual_qty, ordered_qty FROM {table} WHERE item_code = ? AND warehouse = ?",
                (item_code, warehouse),
                as_dict=True
            )
            
            if existing:
                bin_data = existing[0]
                new_reserved = float(bin_data.get('reserved_qty', 0)) + qty
                actual = float(bin_data.get('actual_qty', 0))
                ordered = float(bin_data.get('ordered_qty', 0))
                projected = actual + ordered - new_reserved
                
                db.sql(
                    f"UPDATE {table} SET reserved_qty = ?, projected_qty = ? WHERE name = ?",
                    (new_reserved, projected, bin_data['name'])
                )
                print(f"Reserved {qty} of {item_code} in {warehouse}")

