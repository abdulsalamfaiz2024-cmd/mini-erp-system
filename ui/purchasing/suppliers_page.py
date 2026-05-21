"""
Suppliers Page
Supplier management interface
"""

from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from core.database import get_db


class SuppliersPage(BasePage):
    """Supplier management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Suppliers")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Supplier',
                'command': self.new_supplier,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Edit',
                'command': self.edit_supplier,
                'icon': '✏️',
                'enabled': False,
                'tooltip': 'Select a supplier first'
            },
            {'type': 'separator'},
            {
                'text': 'Refresh',
                'command': self.refresh,
                'icon': '🔄'
            }
        ])
    
    def setup_content(self):
        """Build page content"""
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="🚚 Supplier Directory",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'id', 'text': 'ID', 'width': 100},
            {'name': 'name', 'text': 'Supplier Name', 'width': 250},
            {'name': 'contact', 'text': 'Contact', 'width': 150},
            {'name': 'phone', 'text': 'Phone', 'width': 120},
            {'name': 'email', 'text': 'Email', 'width': 180},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
    
    def load_data(self):
        """Load supplier data"""
        db = get_db()
        
        # Query suppliers (using correct column names)
        try:
            rows = db.fetch_all("""
                SELECT supplier_id, name, contact_person, 
                       phone, email
                FROM suppliers
                WHERE deleted_at IS NULL
                ORDER BY name
                LIMIT 100
            """)
            
            display_data = []
            for row in rows:
                display_data.append((
                    row['supplier_id'],
                    row['name'],
                    row['contact_person'] or 'N/A',
                    row['phone'] or 'N/A',
                    row['email'] or 'N/A'
                ))
            
            self.table.set_data(display_data)
        except:
            # Table doesn't exist or is empty
            self.table.set_data([])
    
    def new_supplier(self):
        """Create new supplier"""
        from ui.purchasing.dialogs import NewSupplierDialog
        dialog = NewSupplierDialog(self)
        self.wait_window(dialog)
        self.refresh()
    
    def edit_supplier(self):
        """Edit selected supplier"""
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a supplier first")
            return
        
        supplier_id = selected['values'][0]
        messagebox.showinfo("Edit", f"Edit dialog for supplier {supplier_id}")
