"""
Accounting Journal Entries Page
Create and post journal entries with double-entry validation

API Bindings:
- AccountingService.create_journal_entry (New Entry)
- AccountingService.post_journal (Post Entry)
- AccountingService.get_general_ledger (Load Data)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from modules.accounting.service import AccountingService
from core.database import get_db
from datetime import date


class JournalEntriesPage(BasePage):
    """Journal entries management"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Journal Entries")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Entry',
                'command': self.new_entry,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Post Entry',
                'command': self.post_entry,
                'icon': '✅',
                'enabled': False,
                'tooltip': 'Select an unposted entry first'
            },
            {'type': 'separator'},
            {
                'text': 'Trial Balance',
                'command': self.show_trial_balance,
                'icon': '⚖️'
            },
        ])
    
    def setup_content(self):
        """Build page content"""
        # Journal entries table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="📒 Journal Entries",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'entry_id', 'text': 'Entry ID', 'width': 150},
            {'name': 'entry_date', 'text': 'Date', 'width': 100},
            {'name': 'description', 'text': 'Description', 'width': 300},
            {'name': 'is_posted', 'text': 'Posted', 'width': 80},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def load_data(self):
        """
        Load journal entries
        API: AccountingService (query journals)
        """
        db = get_db()
        
        sql = """
            SELECT entry_id, entry_date, description, is_posted
            FROM journal_entries
            ORDER BY entry_date DESC
            LIMIT 100
        """
        
        rows = db.fetch_all(sql)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['entry_id'],
                row['entry_date'],
                row['description'],
                '✅ Posted' if row['is_posted'] else '⏳ Unposted'
            ))
        
        self.table.set_data(display_data)
    
    def _on_select(self, event=None):
        """Handle selection"""
        pass
    
    def new_entry(self):
        """
        Create new journal entry
        API: AccountingService.create_journal_entry
        """
        # Simplified dialog - production would have proper debit/credit entry form
        description = simpledialog.askstring("Journal Entry", "Enter description:")
        if not description:
            return
        
        # Simple example: debit cash, credit revenue
        debit_account = simpledialog.askstring("Debit", "Debit account ID:")
        if not debit_account:
            return
        
        amount = simpledialog.askfloat("Amount", "Enter amount:", minvalue=0.01)
        if not amount:
            return
        
        credit_account = simpledialog.askstring("Credit", "Credit account ID:")
        if not credit_account:
            return
        
        lines = [
            {'account_id': debit_account, 'debit': amount, 'credit': 0, 'description': description},
            {'account_id': credit_account, 'debit': 0, 'credit': amount, 'description': description}
        ]
        
        result = self.call_api(
            "AccountingService.create_journal_entry",
            AccountingService.create_journal_entry,
            entry_date=date.today(),
            description=description,
            lines=lines,
            user_id=self.user_data['id'],
            success_msg="Journal entry created"
        )
        
        if result:
            messagebox.showinfo("Created", f"Entry ID: {result}")
            self.refresh()
    
    def post_entry(self):
        """
        Post journal entry (make immutable)
        API: AccountingService.post_journal
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an entry first")
            return
        
        entry_id = selected['values'][0]
        
        if messagebox.askyesno("Confirm", f"Post entry {entry_id}? This cannot be undone."):
            result = self.call_api(
                "AccountingService.post_journal",
                AccountingService.post_journal,
                entry_id,
                self.user_data['id'],
                success_msg=f"Entry {entry_id} posted"
            )
            
            if result is not None:
                self.refresh()
    
    def show_trial_balance(self):
        """
        Show trial balance
        API: AccountingService.get_trial_balance
        """
        result = self.call_api(
            "AccountingService.get_trial_balance",
            AccountingService.get_trial_balance,
            as_of_date=date.today()
        )
        
        if result:
            totals = result.pop('_totals', {})
            msg = f"Trial Balance:\n\n"
            msg += f"Total Debits: ${totals['total_debit'] if totals['total_debit'] else 0:,.2f}\n"
            msg += f"Total Credits: ${totals['total_credit'] if totals['total_credit'] else 0:,.2f}\n"
            msg += f"In Balance: {'✅ Yes' if totals['in_balance'] else '❌ No'}"
            messagebox.showinfo("Trial Balance", msg)
