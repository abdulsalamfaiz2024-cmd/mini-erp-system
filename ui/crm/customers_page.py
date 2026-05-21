"""
Customers Page
Customer management interface using BasePage pattern
"""

from tkinter import ttk
import tkinter as tk
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from core.database import get_db


class CustomersPage(BasePage):
    """Customer management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Customers")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Customer',
                'command': self.new_customer,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Edit Customer',
                'command': self.edit_customer,
                'icon': '✏️',
                'enabled': False,
                'tooltip': 'Select a customer first'
            },
            {
                'text': 'Delete Customer',
                'command': self.delete_customer,
                'icon': '🗑️',
                'enabled': False,
                'tooltip': 'Select a customer first'
            },
            {'type': 'separator'},
            {
                'text': 'Refresh',
                'command': self.refresh,
                'icon': '🔄'
            }
        ])

    def new_customer(self):
        """Create new customer"""
        from ui.sales.dialogs import NewCustomerDialog
        dialog = NewCustomerDialog(self)
        self.wait_window(dialog)
        self.refresh()

    
    def setup_content(self):
        """Build page content"""
        table_frame = ttk. Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="👥 Customer Directory",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'id', 'text': 'ID', 'width': 100},
            {'name': 'name', 'text': 'Name', 'width': 200},
            {'name': 'email', 'text': 'Email', 'width': 180},
            {'name': 'phone', 'text': 'Phone', 'width': 120},
            {'name': 'current_balance', 'text': 'Balance', 'width': 100, 'anchor': 'e'},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
    
    def load_data(self):
        """Load customer data"""
        db = get_db()
        
        rows = db.fetch_all("""
            SELECT customer_id, name, email, phone, current_balance
            FROM customers
            ORDER BY name
            LIMIT 100
        """)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['customer_id'],
                row['name'],
                row['email'] or 'N/A',
                row['phone'] or 'N/A',
                f"${row['current_balance']:,.2f}" if row['current_balance'] else '$0.00'
            ))
        
        self.table.set_data(display_data)

    def _on_select(self, event=None):
        """Handle selection"""
        pass

    def edit_customer(self):
        """Edit selected customer"""
        selected = self.table.get_selected()
        if not selected:
            tk.messagebox.showwarning("No Selection", "Please select a customer first")
            return
            
        customer_id = selected['values'][0]
        tk.messagebox.showinfo("Edit", f"Edit customer {customer_id} (Not implemented)")

    def delete_customer(self):
        """Delete selected customer"""
        selected = self.table.get_selected()
        if not selected:
            tk.messagebox.showwarning("No Selection", "Please select a customer first")
            return
            
        customer_id = selected['values'][0]
        from ui.helpers.confirmation import confirm_delete
        
        if confirm_delete(customer_id, "customer"):
            tk.messagebox.showinfo("Delete", f"Customer {customer_id} deleted (Not implemented)")
            self.refresh()
