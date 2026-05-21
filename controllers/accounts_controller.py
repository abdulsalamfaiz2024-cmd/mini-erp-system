"""
Accounts Controller
Base class for documents that affect accounting (Invoices, Payments).
"""
from controllers.transaction_base import TransactionBase
from core.database import db
import core.frappe as frappe


class AccountsController(TransactionBase):
    """
    Base class for accounting documents.
    Provides:
    - Tax calculation
    - GL Entry creation
    - Payment handling
    """
    
    def validate(self):
        super().validate()
        self.validate_qty_is_not_zero()
        self.calculate_taxes_and_totals()
    
    def validate_qty_is_not_zero(self):
        """Ensure items have quantity"""
        for item in self.get_items():
            qty = float(item.get('qty', 0) or 0)
            if qty <= 0:
                raise ValueError(f"Row {item.get('idx', '?')}: Quantity must be greater than 0")
    
    def calculate_taxes_and_totals(self):
        """Calculate item amounts, taxes, and grand total"""
        total = 0
        net_total = 0
        
        for item in self.get_items():
            qty = float(item.get('qty', 0) or 0)
            rate = float(item.get('rate', 0) or 0)
            amount = qty * rate
            item['amount'] = amount
            total += amount
        
        self._data['total'] = total
        self._data['net_total'] = total
        
        # Apply taxes (simplified)
        taxes = self._data.get('taxes', [])
        total_taxes = 0
        for tax in taxes:
            tax_rate = float(tax.get('rate', 0) or 0)
            tax_amount = total * (tax_rate / 100)
            tax['tax_amount'] = tax_amount
            total_taxes += tax_amount
        
        self._data['total_taxes'] = total_taxes
        self._data['grand_total'] = total + total_taxes
        
        # Apply discount (simplified)
        discount = float(self._data.get('discount_amount', 0) or 0)
        self._data['grand_total'] = self._data['grand_total'] - discount
    
    def make_gl_entries(self, cancel=False):
        """
        Create General Ledger Entries.
        Override in subclasses to define specific accounts.
        """
        # This will be implemented when we have the Account and GL Entry doctypes
        pass
    
    def get_gl_dict(self, args: dict) -> dict:
        """Helper to create GL Entry dict"""
        gl_entry = {
            "doctype": "GL Entry",
            "posting_date": self._data.get('posting_date') or self._data.get('transaction_date'),
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "company": self._data.get('company'),
        }
        gl_entry.update(args)
        return gl_entry
