"""
General Ledger Page
View accounting transactions and balances
"""

from tkinter import ttk
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from core.database import get_db


class LedgerPage(BasePage):
    """General Ledger viewing page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="General Ledger")
    
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
        # Info section
        info_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        info_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(
            info_frame,
            text="📒 General Ledger",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        ttk.Label(
            info_frame,
            text="Accounting transactions and balances",
            font=('Segoe UI', 10)
        ).pack(anchor='w')
        
        # Ledger entries table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        cols = [
            {'name': 'date', 'text': 'Date', 'width': 100},
            {'name': 'entry', 'text': 'Entry #', 'width': 100},
            {'name': 'account', 'text': 'Account', 'width': 200},
            {'name': 'debit', 'text': 'Debit', 'width': 120, 'anchor': 'e'},
            {'name': 'credit', 'text': 'Credit', 'width': 120, 'anchor': 'e'},
            {'name': 'balance', 'text': 'Balance', 'width': 120, 'anchor': 'e'},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
    
    def load_data(self):
        """Load ledger entries"""
        db = get_db()
        
        # Query journal entries (ledger_entries table doesn't exist)
        try:
            rows = db.fetch_all("""
                SELECT entry_id, entry_date, description, 
                       total_debit, total_credit, is_posted
                FROM journal_entries
                WHERE is_posted = 1
                ORDER BY entry_date DESC, entry_id DESC
                LIMIT 100
            """)
            
            display_data = []
            running_balance = 0
            
            for row in rows:
                debit = row['total_debit'] if row['total_debit'] else 0
                credit = row['total_credit'] if row['total_credit'] else 0
                running_balance += (debit - credit)
                
                display_data.append((
                    row['entry_date'],
                    row['entry_id'],
                    row['description'] or 'Journal Entry',
                    f"${debit:,.2f}" if debit else '',
                    f"${credit:,.2f}" if credit else '',
                    f"${running_balance:,.2f}"
                ))
            
            self.table.set_data(display_data)
        except:
            # Table might not have data
            self.table.set_data([])
