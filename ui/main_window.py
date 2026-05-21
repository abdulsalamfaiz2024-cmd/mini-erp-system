"""
Main Application Window
Redesigned with Sidebar Navigation and Page Router
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import Theme


class MainWindow:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Mini-ERP System - {user_data['full_name']}")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 768)
        self.root.state('zoomed')
        
        Theme.apply_styles(self.root)
        
        # Page tracking
        self.current_page = None
        self.current_page_widget = None
        
        self.setup_ui()
        
        # Bind global search (Ctrl+K)
        try:
            from ui.global_search import bind_global_search
            bind_global_search(self.root, self.on_search_select)
        except ImportError:
            pass
    
    def setup_ui(self):
        """Setup main UI structure: Sidebar + Content Area"""
        # Import Sidebar component
        from ui.layout.sidebar import Sidebar
        
        # 1. Sidebar (Left) - Fixed Navigation
        self.sidebar = Sidebar(
            self.root,
            on_navigate=self.load_page,
            user_data=self.user_data
        )
        self.sidebar.pack(side='left', fill='y')
        
        # 2. Content Area (Right) - Dynamic Pages
        self.content_area = ttk.Frame(self.root, style='Main.TFrame')
        self.content_area.pack(side='right', fill='both', expand=True)
        
        # Load default page
        self.load_page('dashboard')
    
    def load_page(self, page_id):
        """
        Page router - maps page_id to page class
        
        Args:
            page_id: Identifier from sidebar (e.g., 'sales_orders', 'invoices')
        """
        # Destroy current page
        if self.current_page_widget:
            self.current_page_widget.destroy()
            self.current_page_widget = None
        
        # Page mapping
        page_map = {
            'dashboard': self.show_dashboard,
            'sales_orders': self.show_sales_orders,
            'invoices': self.show_invoices,
            'returns': self.show_returns,
            'finance': self.show_finance,
            'expenses': self.show_expenses,
            'ledger': self.show_ledger,
            'inventory': self.show_inventory,
            'purchasing': self.show_purchasing,
            'assets': self.show_assets,
            'accounting': self.show_accounting,
            'employees': self.show_employees,
            'customers': self.show_customers,
            'suppliers': self.show_suppliers,
            'reports': self.show_reports,
            'settings': self.show_settings,
        }
        
        # Load page
        page_loader = page_map.get(page_id)
        if page_loader:
            try:
                page_loader()
                self.current_page = page_id
            except Exception as e:
                messagebox.showerror("Page Load Error", f"Failed to load {page_id}: {str(e)}")
                print(f"Error loading page {page_id}: {e}")
                import traceback
                traceback.print_exc()
        else:
            messagebox.showwarning("Not Implemented", f"Page '{page_id}' not yet implemented")
    
    def show_dashboard(self):
        """Show dashboard (fallback to old implementation)"""
        try:
            from ui.modern_dashboard import ModernDashboard
            self.current_page_widget = ModernDashboard(self.content_area, self.user_data)
            self.current_page_widget.pack(fill='both', expand=True)
        except ImportError:
            # Fallback
            label = ttk.Label(self.content_area, text="📊 Dashboard", font=('Segoe UI', 24))
            label.pack(pady=50)
            self.current_page_widget = label
    
    def show_sales_orders(self):
        """Show Sales Orders page (NEW)"""
        from ui.sales.sales_orders_page import SalesOrdersPage
        self.current_page_widget = SalesOrdersPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_invoices(self):
        """Show Invoices page (NEW)"""
        from ui.sales.invoices_page import InvoicesPage
        self.current_page_widget = InvoicesPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_returns(self):
        """Show Returns page"""
        from ui.sales.returns_page import ReturnsPage
        self.current_page_widget = ReturnsPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_finance(self):
        """Show Finance page (NEW)"""
        from ui.finance.finance_page import FinancePage
        self.current_page_widget = FinancePage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_expenses(self):
        """Show Expenses page (NEW)"""
        from ui.finance.expenses_page import ExpensesPage
        self.current_page_widget = ExpensesPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_ledger(self):
        """Show Ledger page (NEW)"""
        from ui.finance.ledger_page import LedgerPage
        self.current_page_widget = LedgerPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_inventory(self):
        """Show Inventory page (NEW)"""
        from ui.inventory.inventory_stock_page import InventoryStockPage
        self.current_page_widget = InventoryStockPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_purchasing(self):
        """Show Purchasing page"""
        from ui.purchasing.purchasing_page import PurchasingPage
        self.current_page_widget = PurchasingPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_assets(self):
        """Show Assets page"""
        from ui.assets.assets_page import AssetsPage
        self.current_page_widget = AssetsPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_accounting(self):
        """Show Accounting/Journal Entries page (NEW)"""
        from ui.accounting.journal_entries_page import JournalEntriesPage
        self.current_page_widget = JournalEntriesPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_employees(self):
        """Show Employees page (NEW)"""
        from ui.admin.employees_page import EmployeesPage
        self.current_page_widget = EmployeesPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_customers(self):
        """Show Customers page"""
        from ui.crm.customers_page import CustomersPage
        self.current_page_widget = CustomersPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_suppliers(self):
        """Show Suppliers page (NEW)"""
        from ui.purchasing.suppliers_page import SuppliersPage
        self.current_page_widget = SuppliersPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_reports(self):
        """Show Reports page"""
        from ui.reports.reports_page import ReportsPage
        self.current_page_widget = ReportsPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def show_settings(self):
        """Show Settings page"""
        from ui.admin.settings_page import SettingsPage
        self.current_page_widget = SettingsPage(self.content_area, self.user_data)
        self.current_page_widget.pack(fill='both', expand=True)
    
    def _show_placeholder(self, page_name, message=""):
        """Show placeholder for unimplemented/error pages"""
        frame = ttk.Frame(self.content_area, style='Card.TFrame')
        frame.pack(fill='both', expand=True, padx=50, pady=50)
        
        ttk.Label(
            frame,
            text=f"⚠️ {page_name}",
            font=('Segoe UI', 24, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            frame,
            text=message or f"{page_name} page is under construction",
            font=('Segoe UI', 12)
        ).pack(pady=10)
        
        self.current_page_widget = frame
    
    def on_search_select(self, result):
        """Handle global search result selection"""
        # Implement navigation based on search result
        if result.get('type') == 'order':
            self.load_page('sales_orders')
        elif result.get('type') == 'customer':
            self.load_page('customers')
        # Add more mappings as needed
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Would trigger return to login screen
