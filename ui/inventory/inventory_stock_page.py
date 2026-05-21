"""
Inventory Stock Levels Page
Main inventory management with issue orders and counts

API Bindings:
- InventoryManager.add_stock (Add Stock)
- IssueOrderService.create_issue (Issue Order)
- InventoryCountService.start_count (Start Count)
- InventoryManager.get_stock_level (Load Data)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from modules.inventory.inventory_manager import InventoryManager
from modules.inventory.issue_service import IssueOrderService
from modules.inventory.count_service import InventoryCountService
from core.database import get_db
from datetime import date


class InventoryStockPage(BasePage):
    """Inventory stock levels and operations"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Inventory - Stock Levels")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'Add Stock',
                'command': self.add_stock,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Issue Order',
                'command': self.create_issue,
                'icon': '📦'
            },
            {
                'text': 'Start Count',
                'command': self.start_count,
                'icon': '📊'
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
        # Stock table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="📦 Stock Levels",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'product_id', 'text': 'Product ID', 'width': 120},
            {'name': 'product_name', 'text': 'Product', 'width': 200},
            {'name': 'quantity', 'text': 'Qty', 'width': 80, 'anchor': 'e'},
            {'name': 'warehouse', 'text': 'Warehouse', 'width': 120},
            {'name': 'cost_price', 'text': 'Cost', 'width': 100, 'anchor': 'e'},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
    
    def load_data(self):
        """
        Load stock levels
        API: InventoryManager.get_stock_level (indirectly via query)
        """
        db = get_db()
        
        sql = """
            SELECT 
                i.product_id,
                p.name as product_name,
                SUM(i.quantity) as total_qty,
                i.warehouse_id,
                i.cost_price
            FROM inventory i
            LEFT JOIN products p ON i.product_id = p.product_id
            GROUP BY i.product_id, i.warehouse_id
            ORDER BY p.name
        """
        
        rows = db.fetch_all(sql)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['product_id'],
                row['product_name'] or 'Unknown',
                row['total_qty'],
                f"WH-{row['warehouse_id']}",
                f"${row['cost_price']:,.2f}"
            ))
        
        self.table.set_data(display_data)
    
    def add_stock(self):
        """
        Add stock with smart product lookup dialog
        API: InventoryManager.add_stock
        """
        # Create Add Stock dialog with SmartLookupField
        dialog = tk.Toplevel(self)
        dialog.title("Add Stock")
        dialog.geometry("450x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # Apply styling
        dialog.configure(bg='white')
        
        content = tk.Frame(dialog, bg='white', padx=30, pady=20)
        content.pack(fill='both', expand=True)
        
        tk.Label(content, text="Add Stock", font=("Segoe UI", 16, "bold"), 
                 bg='white', fg='#111827').pack(anchor='w', pady=(0, 20))
        
        # Product lookup with autocomplete
        try:
            from ui.widgets.smart_lookup import SmartLookupField
            from modules.lookup_service import LookupService
            
            prod_id_var = tk.StringVar()
            prod_name_var = tk.StringVar()
            
            product_lookup = SmartLookupField(
                content,
                label="Product",
                data_source=LookupService.get_products,
                id_var=prod_id_var,
                name_var=prod_name_var,
                placeholder="Search product by name or ID...",
                required=True
            )
            product_lookup.pack(fill='x', pady=(0, 15))
            
        except ImportError:
            # Fallback to basic entry
            prod_id_var = tk.StringVar()
            tk.Label(content, text="Product ID:", bg='white').pack(anchor='w')
            ttk.Entry(content, textvariable=prod_id_var).pack(fill='x', pady=(0, 15))
        
        # Quantity
        qty_var = tk.StringVar(value="1")
        tk.Label(content, text="Quantity *", font=("Segoe UI", 10), 
                 bg='white', fg='#374151').pack(anchor='w')
        ttk.Entry(content, textvariable=qty_var).pack(fill='x', pady=(0, 15))
        
        # Cost Price
        cost_var = tk.StringVar()
        tk.Label(content, text="Cost Price ($) *", font=("Segoe UI", 10), 
                 bg='white', fg='#374151').pack(anchor='w')
        ttk.Entry(content, textvariable=cost_var).pack(fill='x', pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill='x', pady=(10, 0))
        
        def save():
            product_id = prod_id_var.get()
            if not product_id:
                messagebox.showerror("Error", "Please select a product.")
                return
                
            try:
                quantity = int(qty_var.get())
                cost_price = float(cost_var.get())
                if quantity <= 0:
                    raise ValueError("Quantity must be positive")
                if cost_price <= 0:
                    raise ValueError("Cost price must be positive")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
                return
            
            result = self.call_api(
                "InventoryManager.add_stock",
                InventoryManager.add_stock,
                product_id=product_id,
                quantity=quantity,
                cost_price=cost_price,
                user_id=self.user_data['id'],
                success_msg=f"Added {quantity} units of {product_id}"
            )
            
            if result is not None:
                dialog.destroy()
                self.refresh()
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Add Stock", style='Success.TButton', command=save).pack(side='right')

    
    def create_issue(self):
        """
        Create issue order
        API: IssueOrderService.create_issue
        """
        sales_order = simpledialog.askstring("Issue Order", "Enter sales order ID:")
        if not sales_order:
            return
        
        # Simplified - would have proper dialog
        messagebox.showinfo("Info", "Issue order creation requires full dialog implementation")
    
    def start_count(self):
        """
        Start inventory count
        API: InventoryCountService.start_count
        """
        warehouse = simpledialog.askinteger("Count", "Enter warehouse ID:", minvalue=1)
        if not warehouse:
            return
        
        employee_id = self.get_employee_id()
        if not employee_id:
            messagebox.showerror("Error", "No employee ID")
            return
        
        result = self.call_api(
            "InventoryCountService.start_count",
            InventoryCountService.start_count,
            count_date=date.today(),
            warehouse_id=warehouse,
            employee_id=employee_id,
            user_id=self.user_data['id'],
            success_msg="Inventory count started"
        )
        
        if result:
            messagebox.showinfo("Count Started", f"Count ID: {result}")
    
    def export_data(self):
        """Export stock data"""
        from tkinter import filedialog
        from modules.reporting.reporting_manager import ReportingManager
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not filepath:
            return
        
        db = get_db()
        rows = db.fetch_all("SELECT * FROM inventory")
        
        self.call_api(
            "ReportingManager.export_to_csv",
            ReportingManager.export_to_csv,
            rows,
            filepath,
            success_msg=f"Stock data exported"
        )
