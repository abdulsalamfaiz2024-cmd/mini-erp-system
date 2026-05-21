"""
Invoices Page
Manage invoiced sales orders and payment recording

API Bindings:
- SalesManager.record_payment (Record Payment button)
- ReportingManager.export_pdf_table (Print button)
- ReportingManager.export_to_csv (Export button)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from modules.sales.sales_manager import SalesManager
from modules.reporting.reporting_manager import ReportingManager
from core.database import get_db


class InvoicesPage(BasePage):
    """Invoices and payments management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Invoices")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'Record Payment',
                'command': self.record_payment,
                'icon': '💰',
                'style': 'Success.TButton',
                'enabled': False,
                'tooltip': 'Select an invoice first'
            },
            {
                'text': 'Print',
                'command': self.print_invoice,
                'icon': '🖨️',
                'enabled': False,
                'tooltip': 'Select an invoice first'
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
        # Invoices table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="🧾 All Invoices",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'order_number', 'text': 'Invoice #', 'width': 120},
            {'name': 'order_date', 'text': 'Date', 'width': 100},
            {'name': 'customer', 'text': 'Customer', 'width': 200},
            {'name': 'total', 'text': 'Amount', 'width': 100, 'anchor': 'e'},
            {'name': 'paid', 'text': 'Paid', 'width': 100, 'anchor': 'e'},
            {'name': 'balance', 'text': 'Balance', 'width': 100, 'anchor': 'e'},
            {'name': 'status', 'text': 'Status', 'width': 100}
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def load_data(self):
        """Load invoices"""
        db = get_db()
        
        sql = """
            SELECT 
                so.order_number,
                so.order_date,
                c.name as customer,
                so.total_amount,
                COALESCE(SUM(p.amount), 0) as paid_amount,
                so.status
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.customer_id
            LEFT JOIN payments p ON p.entity_id = so.order_number AND p.entity_type = 'sales_order'
            WHERE so.status IN ('invoiced', 'paid', 'completed')
            GROUP BY so.order_number
            ORDER BY so.order_date DESC
            LIMIT 100
        """
        
        rows = db.fetch_all(sql)
        
        display_data = []
        for row in rows:
            total = row['total_amount']
            paid = row['paid_amount'] or 0
            balance = total - paid
            
            display_data.append((
                row['order_number'],
                row['order_date'],
                row['customer'] or 'Unknown',
                f"${total:,.2f}",
                f"${paid:,.2f}",
                f"${balance:,.2f}",
                row['status']
            ))
        
        self.table.set_data(display_data)
    
    def _on_select(self, event=None):
        """Handle selection"""
        selected = self.table.get_selected()
        
        actions = []
        if selected:
            # Check balance
            balance_str = selected['values'][5].replace('$', '').replace(',', '')
            try:
                balance = float(balance_str)
            except ValueError:
                balance = 0
            
            if balance > 0:
                 actions.append({
                    'text': 'Record Payment',
                    'command': self.record_payment,
                    'icon': '💰',
                    'style': 'Success.TButton'
                })
            
            actions.append({
                'text': 'Print',
                'command': self.print_invoice,
                'icon': '🖨️'
            })
            
        actions.append({'type': 'separator'})
        actions.append({
            'text': 'Export',
            'command': self.export_data,
            'icon': '📑'
        })
        
        self.topbar.set_actions(actions)
    
    def record_payment(self):
        """
        Record payment
        API: SalesManager.record_payment
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an invoice first")
            return
        
        order_number = selected['values'][0]
        balance = float(selected['values'][5].replace('$', '').replace(',', ''))
        
        # Simple payment dialog
        from ui.finance_ui import PaymentApprovalDialog
        
        # Reuse payment dialog but adapt for direct payment
        # (Simplified - would create dedicated payment dialog)
        if balance <= 0:
            messagebox.showinfo("Paid", "This invoice is already paid in full")
            return
        
        amount = tk.simpledialog.askfloat("Payment", f"Enter payment amount (Balance: ${balance:,.2f}):", minvalue=0.01, maxvalue=balance)
        if amount:
            from ui.helpers.confirmation import confirm_action
            if not confirm_action("Record Payment", order_number, f"Amount: ${amount:,.2f}"):
                return

            result = self.call_api(
                "SalesManager.record_payment",
                SalesManager.record_payment,
                order_number,
                amount,
                "Cash",  # Could ask for method
                self.user_data['id'],
                success_msg=f"Payment of ${amount:,.2f} recorded"
            )
            
            if result is not None:
                self.refresh()
    
    def print_invoice(self):
        """
        Print invoice as PDF
        API: ReportingManager.export_pdf_table
        """
        from tkinter import filedialog
        
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an invoice first")
            return
        
        order_number = selected['values'][0]
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Invoice_{order_number}.pdf"
        )
        
        if not filepath:
            return
        
        # Get invoice details
        db = get_db()
        order = db.fetch_one("SELECT * FROM sales_orders WHERE order_number=?", (order_number,))
        items = db.fetch_all("SELECT * FROM sales_order_items WHERE order_number=?", (order_number,))
        
        # Build PDF data
        headers = ['Product', 'Qty', 'Price', 'Total']
        data_rows = [[i['product_id'], i['quantity'], f"${i['unit_price']:.2f}", f"${i['line_total']:.2f}"] for i in items]
        
        result = self.call_api(
            "ReportingManager.export_pdf_table",
            ReportingManager.export_pdf_table,
            f"Invoice {order_number}",
            headers,
            data_rows,
            filepath,
            totals={'Total': f"${order['total_amount']:.2f}"},
            success_msg=f"Invoice saved to {filepath}"
        )
    
    def export_data(self):
        """Export invoices to CSV"""
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not filepath:
            return
        
        db = get_db()
        rows = db.fetch_all("SELECT * FROM sales_orders WHERE status IN ('invoiced', 'paid', 'completed') ORDER BY order_date DESC")
        
        result = self.call_api(
            "ReportingManager.export_to_csv",
            ReportingManager.export_to_csv,
            rows,
            filepath,
            success_msg=f"Invoices exported to {filepath}"
        )
