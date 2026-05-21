"""
Sales Orders Page
Main page for managing sales orders with full workflow visibility

API Bindings:
- SalesOrderService.create_order (New Order button)
- SalesOrderService.submit_order (Submit button)  
- SalesManager.generate_invoice (Invoice button)
- ReportingManager.export_to_csv (Export button)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from ui.workflow_widgets import WorkflowStatusLabel
from modules.sales.service import SalesOrderService
from modules.sales.sales_manager import SalesManager
from modules.reporting.reporting_manager import ReportingManager
from core.database import get_db


class SalesOrdersPage(BasePage):
    """Sales Orders management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Sales Orders")
        
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Order',
                'command': self.new_order,
                'icon': '🆕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Submit',
                'command': self.submit_order,
                'icon': '📤',
                'enabled': False,
                'tooltip': 'Select a draft order first'
            },
            {
                'text': 'Invoice',
                'command': self.generate_invoice,
                'icon': '🧾',
                'enabled': False,
                'tooltip': 'Select a completed order first'
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
        # Orders table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="📋 All Sales Orders",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        # Table columns
        cols = [
            {'name': 'order_number', 'text': 'Order #', 'width': 120},
            {'name': 'order_date', 'text': 'Date', 'width': 100},
            {'name': 'customer', 'text': 'Customer', 'width': 200},
            {'name': 'total', 'text': 'Amount', 'width': 100, 'anchor': 'e'},
            {'name': 'workflow_state', 'text': 'State', 'width': 150},
            {'name': 'status', 'text': 'Status', 'width': 100},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        # Enable row selection
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.table.tree.bind('<Double-Button-1>', self._on_double_click)
    
    def load_data(self):
        """Load sales orders from database"""
        db = get_db()
        
        # Query with workflow state
        sql = """
            SELECT 
                so.order_number,
                so.order_date,
                c.name as customer,
                so.total_amount,
                ws.name as workflow_state,
                so.status
            FROM sales_orders so
            LEFT JOIN customers c ON so.customer_id = c.customer_id
            LEFT JOIN document_state_tracker dst ON dst.document_id = so.order_number
            LEFT JOIN workflow_states ws ON dst.current_state_id = ws.state_id
            WHERE dst.document_type = 'SALES_ORDER' OR dst.document_type IS NULL
            ORDER BY so.order_date DESC
            LIMIT 100
        """
        
        rows = db.fetch_all(sql)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['order_number'],
                row['order_date'],
                row['customer'] or 'Unknown',
                f"${row['total_amount']:,.2f}",
                row['workflow_state'] or 'No State',
                row['status']
            ))
        
        self.table.set_data(display_data)
    
    def _on_select(self, event=None):
        """Handle row selection - enable/disable buttons"""
        selected = self.table.get_selected()
        if not selected:
            # Disable action buttons
            return
        
        # Get order details
        order_number = selected['values'][0]
        workflow_state = selected['values'][4]
        
        # Update button states based on workflow
        # Submit enabled if Draft
        # Invoice enabled if Completed
        # (Simplified - would check actual state)
    
    def _on_double_click(self, event=None):
        """View/edit order on double-click"""
        selected = self.table.get_selected()
        if not selected:
            return
        
        order_number = selected['values'][0]
        self.view_order(order_number)
    
    def new_order(self):
        """
        Create new sales order
        API: SalesOrderService.create_order
        """
        # Import here to avoid circular imports
        from ui.sales.dialogs import NewOrderDialog
        
        dialog = NewOrderDialog(self, self.user_data)
        self.wait_window(dialog)
        self.refresh()
    
    def submit_order(self):
        """
        Submit selected order
        API: SalesOrderService.submit_order
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        order_number = selected['values'][0]
        employee_id = self.get_employee_id()
        
        if not employee_id:
            messagebox.showerror("Error", "No employee ID linked to your account")
            return
        
        if messagebox.askyesno("Confirm", f"Submit order {order_number}?"):
            result = self.call_api(
                "SalesOrderService.submit_order",
                SalesOrderService.submit_order,
                order_number,
                employee_id,
                success_msg=f"Order {order_number} submitted successfully"
            )
            
            if result is not None:
                self.refresh()
    
    def generate_invoice(self):
        """
        Generate invoice for selected order
        API: SalesManager.generate_invoice
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an order first")
            return
        
        order_number = selected['values'][0]
        
        if messagebox.askyesno("Confirm", f"Generate invoice for {order_number}?"):
            result = self.call_api(
                "SalesManager.generate_invoice",
                SalesManager.generate_invoice,
                order_number,
                self.user_data['id'],
                success_msg=f"Invoice generated for {order_number}"
            )
            
            if result is not None:
                self.refresh()
    
    def export_data(self):
        """
        Export orders to CSV
        API: ReportingManager.export_to_csv
        """
        from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not filepath:
            return
        
        # Get data
        db = get_db()
        rows = db.fetch_all("SELECT * FROM sales_orders ORDER BY order_date DESC")
        
        result = self.call_api(
            "ReportingManager.export_to_csv",
            ReportingManager.export_to_csv,
            rows,
            filepath,
            success_msg=f"Data exported to {filepath}"
        )
    
    def view_order(self, order_number):
        """View order details"""
        from ui.sales.dialogs import ViewOrderDialog
        
        dialog = ViewOrderDialog(self, order_number, self.user_data)
        self.wait_window(dialog)
        self.refresh()
