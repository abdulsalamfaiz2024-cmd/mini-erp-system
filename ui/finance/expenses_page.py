"""
Finance Expenses Page
Manage all expenses with approval workflow

API Bindings:
- ExpenseService.record_expense (New Expense)
- ExpenseService.approve_expense (Approve)
- ReportingManager.export_to_csv (Export)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from modules.finance.expense_service import ExpenseService
from modules.reporting.reporting_manager import ReportingManager
from core.database import get_db


class ExpensesPage(BasePage):
    """Expense management and approval page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Expenses")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Expense',
                'command': self.new_expense,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Approve',
                'command': self.approve_expense,
                'icon': '✅',
                'enabled': False,
                'tooltip': 'Select a pending expense first'
            },
            {'type': 'separator'},
            {
                'text': 'Export',
                'command': self.export_data,
                'icon': '📑'
            },
        ])
    
    def setup_content(self):
        """Build page content"""
        # Expenses table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="💸 All Expenses",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'expense_id', 'text': 'ID', 'width': 120},
            {'name': 'date', 'text': 'Date', 'width': 100},
            {'name': 'category', 'text': 'Category', 'width': 150},
            {'name': 'amount', 'text': 'Amount', 'width': 100, 'anchor': 'e'},
            {'name': 'description', 'text': 'Description', 'width': 250},
            {'name': 'status', 'text': 'Status', 'width': 120},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def load_data(self):
        """Load expenses"""
        db = get_db()
        
        sql = """
            SELECT expense_id, date, category, amount, description, status
            FROM expenses
            ORDER BY date DESC
            LIMIT 100
        """
        
        rows = db.fetch_all(sql)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['expense_id'],
                row['date'],
                row['category'],
                f"${row['amount']:,.2f}",
                row['description'][:50],
                row['status'] if 'status' in row.keys() else 'approved'
            ))
        
        self.table.set_data(display_data)
    
    def _on_select(self, event=None):
        """Handle selection"""
        pass
    
    def new_expense(self):
        """
        Create new expense
        API: ExpenseService.record_expense
        """
        # Simple dialog for expense entry
        category = simpledialog.askstring("Expense", "Enter category:")
        if not category:
            return
        
        amount = simpledialog.askfloat("Expense", "Enter amount:", minvalue=0.01)
        if not amount:
            return
        
        description = simpledialog.askstring("Expense", "Enter description:")
        if not description:
            return
        
        employee_id = self.get_employee_id()
        if not employee_id:
            messagebox.showerror("Error", "No employee ID linked")
            return
        
        result = self.call_api(
            "ExpenseService.record_expense",
            ExpenseService.record_expense,
            expense_type='variable',
            category=category,
            amount=amount,
            description=description,
            employee_id=employee_id,
            user_id=self.user_data['id'],
            success_msg=f"Expense ${amount:,.2f} recorded"
        )
        
        if result is not None:
            self.refresh()
    
    def approve_expense(self):
        """
        Approve selected expense
        API: ExpenseService.approve_expense
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an expense first")
            return
        
        expense_id = selected['values'][0]
        employee_id = self.get_employee_id()
        
        # Use standardized confirmation helper
        from ui.helpers.confirmation import confirm_approve
        
        if confirm_approve(expense_id, "expense"):
            result = self.call_api(
                "ExpenseService.approve_expense",
                ExpenseService.approve_expense,
                expense_id,
                employee_id,
                self.user_data['id'],
                success_msg=f"Expense {expense_id} approved"
            )
            
            if result is not None:
                self.refresh()
    
    def export_data(self):
        """Export expenses to CSV"""
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not filepath:
            return
        
        db = get_db()
        rows = db.fetch_all("SELECT * FROM expenses ORDER BY date DESC")
        
        self.call_api(
            "ReportingManager.export_to_csv",
            ReportingManager.export_to_csv,
            rows,
            filepath,
            success_msg=f"Expenses exported to {filepath}"
        )
