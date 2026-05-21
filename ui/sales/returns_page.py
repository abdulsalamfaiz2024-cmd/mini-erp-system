"""
Sales Returns Page
Manage sales returns with workflow tracking
"""

from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from modules.sales.service import SalesOrderService  # Returns service in same module
from core.database import get_db


class ReturnsPage(BasePage):
    """Sales returns management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Sales Returns")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Return',
                'command': self.create_return,
                'icon': '↩️',
                'style': 'Primary.TButton'
            },
            {
                'text': 'Submit',
                'command': self.submit_return,
                'icon': '📤',
                'enabled': False,
                'tooltip': 'Select a pending return first'
            },
            {
                'text': 'Approve',
                'command': self.approve_return,
                'icon': '✅',
                'enabled': False,
                'tooltip': 'Select a submitted return first'
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
            text="↩️ Sales Returns",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'return_id', 'text': 'Return ID', 'width': 120},
            {'name': 'order_number', 'text': 'Original Order', 'width': 120},
            {'name': 'date', 'text': 'Date', 'width': 100},
            {'name': 'customer', 'text': 'Customer', 'width': 180},
            {'name': 'amount', 'text': 'Amount', 'width': 100, 'anchor': 'e'},
            {'name': 'status', 'text': 'Status', 'width': 120},
            {'name': 'reason', 'text': 'Reason', 'width': 200},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        # Enable row selection
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def load_data(self):
        """Load returns data"""
        db = get_db()
        
        # Check if table exists
        try:
            sql = """
                SELECT sr.return_id, sr.order_number, sr.return_date, 
                       c.name as customer, sr.refund_amount, 
                       ws.name as status, sr.reason
                FROM sales_returns sr
                LEFT JOIN sales_orders so ON sr.order_number = so.order_number
                LEFT JOIN customers c ON so.customer_id = c.customer_id
                LEFT JOIN document_state_tracker dst ON dst.document_id = sr.return_id
                LEFT JOIN workflow_states ws ON dst.current_state_id = ws.state_id
                WHERE dst.document_type = 'SALES_RETURN' OR dst.document_type IS NULL
                ORDER BY sr.return_date DESC
                LIMIT 100
            """
            
            rows = db.fetch_all(sql)
            
            display_data = []
            for row in rows:
                display_data.append((
                    row['return_id'],
                    row['order_number'],
                    row['return_date'],
                    row['customer'] or 'Unknown',
                    f"${row['refund_amount']:,.2f}" if row['refund_amount'] else '$0.00',
                    row['status'] or 'Pending',
                    row['reason'] or 'N/A'
                ))
            
            self.table.set_data(display_data)
        except Exception as e:
            # Table might not exist yet
            self.table.set_data([])
    
    def _on_select(self, event=None):
        """Handle row selection - enable/disable buttons"""
        selected = self.table.get_selected()
        # Would update button states based on workflow status
        pass
    
    def create_return(self):
        """
        Create new sales return
        API: SalesReturnService.create_return
        """
        messagebox.showinfo(
            "Create Return",
            "Return creation dialog will be implemented.\n\n"
            "API: SalesReturnService.create_return\n"
            "Workflow: SALES_RETURN → Pending state"
        )
    
    def submit_return(self):
        """
        Submit return for approval
        API: SalesReturnService.submit_return
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a return first")
            return
        
        return_id = selected['values'][0]
        
        from ui.helpers.confirmation import confirm_submit
        
        if confirm_submit(return_id, "return"):
            messagebox.showinfo(
                "Submit Return",
                f"Submit return {return_id} functionality will be implemented.\n\n"
                "API: SalesReturnService.submit_return\n"
                "Status: Pending implementation"
            )
    
    def approve_return(self):
        """
        Approve sales return
        API: SalesReturnService.approve_return
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a return first")
            return
        
        return_id = selected['values'][0]
        
        from ui.helpers.confirmation import confirm_approve
        
        if confirm_approve(return_id, "return"):
            messagebox.showinfo(
                "Approve Return",
                f"Approve return {return_id} functionality will be implemented.\n\n"
                "API: SalesReturnService.approve_return\n"
                "Status: Pending implementation"
            )
