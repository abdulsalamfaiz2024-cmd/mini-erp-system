"""
Transaction Base Controller
Base class for all transactional documents (Orders, Invoices, etc.)
Implements common lifecycle hooks and utility methods.
"""
from core.doctype import Document
from core.database import db
import core.frappe as frappe
from datetime import datetime


class TransactionBase(Document):
    """
    Base class for all transaction documents.
    Provides:
    - Lifecycle hooks (before_validate, validate, before_save, on_submit, on_cancel)
    - Total calculations
    - Status management
    """
    
    def __init__(self, doctype: str, name: str = None, **kwargs):
        super().__init__(doctype, name, **kwargs)
        self.flags = {}  # Transient flags for document processing
    
    # ========== LIFECYCLE HOOKS ==========
    
    def save(self):
        """Enhanced save with lifecycle hooks"""
        self.run_method("before_validate")
        self.run_method("validate")
        self.run_method("before_save")
        
        # Call parent save (handles DB persistence)
        result = super().save()
        
        self.run_method("after_save")
        return result
    
    def submit(self):
        """Submit document (lock it)"""
        if self.docstatus == 1:
            raise ValueError(f"{self.doctype} {self.name} is already submitted")
        
        self.run_method("before_submit")
        self.docstatus = 1
        self._data['docstatus'] = 1
        super().save()  # Just save, don't re-run validate
        self.run_method("on_submit")
        db.commit()
        return self
    
    def cancel(self):
        """Cancel submitted document"""
        if self.docstatus != 1:
            raise ValueError(f"{self.doctype} {self.name} is not submitted")
        
        self.run_method("before_cancel")
        self.docstatus = 2
        self._data['docstatus'] = 2
        super().save()
        self.run_method("on_cancel")
        db.commit()
        return self
    
    def run_method(self, method_name: str, *args, **kwargs):
        """Run a method if it exists on the document"""
        method = getattr(self, method_name, None)
        if method and callable(method):
            return method(*args, **kwargs)
        return None
    
    # ========== DEFAULT HOOKS (Override in subclasses) ==========
    
    def before_validate(self):
        """Called before validation. Set defaults here."""
        pass
    
    def validate(self):
        """Validate document. Raise exceptions on errors."""
        pass
    
    def before_save(self):
        """Called after validation, before save."""
        pass
    
    def after_save(self):
        """Called after save."""
        pass
    
    def before_submit(self):
        """Called before submit."""
        pass
    
    def on_submit(self):
        """Called after submit. Create stock/GL entries here."""
        pass
    
    def before_cancel(self):
        """Called before cancel."""
        pass
    
    def on_cancel(self):
        """Called after cancel. Reverse entries here."""
        pass
    
    # ========== UTILITY METHODS ==========
    
    def set_status(self, status: str = None):
        """Set document status"""
        if status:
            self._data['status'] = status
        else:
            # Auto-determine status based on docstatus
            if self.docstatus == 0:
                self._data['status'] = "Draft"
            elif self.docstatus == 1:
                self._data['status'] = "Submitted"
            elif self.docstatus == 2:
                self._data['status'] = "Cancelled"
    
    def calculate_totals(self):
        """Calculate totals from items. Override in subclasses."""
        total = 0
        total_qty = 0
        
        items = self._data.get('items', [])
        for item in items:
            amount = float(item.get('amount', 0) or 0)
            qty = float(item.get('qty', 0) or 0)
            total += amount
            total_qty += qty
        
        self._data['total'] = total
        self._data['total_qty'] = total_qty
        self._data['grand_total'] = total  # Can be overridden for taxes
    
    def get_items(self):
        """Get child items"""
        return self._data.get('items', [])
    
    def append(self, fieldname: str, item_data: dict):
        """Append a child item"""
        if fieldname not in self._data:
            self._data[fieldname] = []
        self._data[fieldname].append(item_data)
