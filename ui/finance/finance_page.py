"""
Finance Page
Simplified finance management interface using BasePage pattern
"""

from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from modules.finance.finance_manager import FinanceManager
from core.database import get_db


class FinancePage(BasePage):
    """Finance management page - simplified placeholder"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Finance")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'Refresh',
                'command': self.refresh,
                'icon': '🔄'
            }
        ])
    
    def setup_content(self):
        """Build page content"""
        # Dashboard metrics
        metrics_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        metrics_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(
            metrics_frame,
            text="📊 Finance Dashboard",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 20))
        
        # Metrics grid
        self.lbl_cash = ttk.Label(metrics_frame, text="Cash Flow: Loading...", font=('Segoe UI', 11))
        self.lbl_cash.pack(anchor='w', pady=5)
        
        self.lbl_ar = ttk.Label(metrics_frame, text="Accounts Receivable: Loading...", font=('Segoe UI', 11))
        self.lbl_ar.pack(anchor='w', pady=5)
        
        self.lbl_ap = ttk.Label(metrics_frame, text="Accounts Payable: Loading...", font=('Segoe UI', 11))
        self.lbl_ap.pack(anchor='w', pady=5)
        
        # Pending approvals table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ttk.Label(
            table_frame,
            text="💼 Pending Finance Approvals",
            style='CardTitle.TLabel',
           font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'order', 'text': 'Order #', 'width': 120},
            {'name': 'date', 'text': 'Date', 'width': 100},
            {'name': 'customer', 'text': 'Customer', 'width': 200},
            {'name': 'amount', 'text': 'Amount', 'width': 100, 'anchor': 'e'},
            {'name': 'state', 'text': 'State', 'width': 150},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
    
    def load_data(self):
        """Load finance data"""
        # Load metrics using standardized API calls
        cash_flow = self.call_api(
            "FinanceManager.get_cash_flow",
            FinanceManager.get_cash_flow
        )
        
        ar = self.call_api(
            "FinanceManager.get_accounts_receivable",
            FinanceManager.get_accounts_receivable
        )
        
        ap = self.call_api(
            "FinanceManager.get_accounts_payable",
            FinanceManager.get_accounts_payable
        )
        
        # Update metrics
        if cash_flow:
            self.lbl_cash.configure(text=f"Cash Flow: ${cash_flow:,.2f}")
        
        if ar:
            self.lbl_ar.configure(text=f"Accounts Receivable: ${ar:,.2f}")
        
        if ap:
            self.lbl_ap.configure(text=f"Accounts Payable: ${ap:,.2f}")
        
        # Load pending approvals
        db = get_db()
        sql = """
            SELECT so.order_number, so.order_date, c.name, so.total_amount, ws.name as state
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.customer_id
            LEFT JOIN document_state_tracker dst ON dst.document_id = so.order_number
            LEFT JOIN workflow_states ws ON dst.current_state_id = ws.state_id
            WHERE ws.name = 'Submitted' AND dst.document_type = 'SALES_ORDER'
            ORDER BY so.order_date DESC
            LIMIT 50
        """
        
        rows = db.fetch_all(sql)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['order_number'],
                row['order_date'],
                row['name'] or 'Unknown',
                f"${row['total_amount']:,.2f}",
                row['state'] or 'Draft'
            ))
        
        self.table.set_data(display_data)
