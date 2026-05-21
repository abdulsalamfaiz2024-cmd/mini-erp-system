"""
Purchasing Page
Simplified purchasing management interface using BasePage pattern
"""

from tkinter import ttk
from ui.layout.base_page import BasePage  
from ui.modern_widgets import ModernTable
from core.database import get_db


class PurchasingPage(BasePage):
    """Purchasing management page - simplified placeholder"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Purchasing")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Purchase Order',
                'command': self.new_order,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Refresh',
                'command': self.refresh,
                'icon': '🔄'
            }
        ])

    def new_order(self):
        """Create new purchase order"""
        from ui.purchasing.dialogs import NewPurchaseOrderDialog
        dialog = NewPurchaseOrderDialog(self, self.user_data)
        self.wait_window(dialog)
        self.refresh()

    
    def setup_content(self):
        """Build page content"""
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="📦 Purchase Orders",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'po', 'text': 'PO #', 'width': 120},
            {'name': 'date', 'text': 'Date', 'width': 100},
            {'name': 'supplier', 'text': 'Supplier', 'width': 200},
            {'name': 'amount', 'text': 'Amount', 'width': 100, 'anchor': 'e'},
            {'name': 'status', 'text': 'Status', 'width': 100},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
    
    def load_data(self):
        """Load purchasing data"""
        db = get_db()
        
        # Check if table exists
        try:
            rows = db.fetch_all("""
                SELECT po_number, order_date, 'Supplier' as supplier, 
                       total_amount, status
                FROM purchase_orders
                ORDER BY order_date DESC
                LIMIT 50
            """)
            
            display_data = []
            for row in rows:
                display_data.append((
                    row['po_number'],
                    row['order_date'],
                    row['supplier'],
                    f"${row['total_amount']:,.2f}",
                    row['status']
                ))
            
            self.table.set_data(display_data)
        except:
            # Table doesn't exist - show empty
            self.table.set_data([])
