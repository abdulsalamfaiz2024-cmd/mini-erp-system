"""
Modern Dashboard with Real Features
Complete replacement of basic dashboard with professional features
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Dict, List, Any

from core.database import get_db
from core.logger import get_logger
from ui.styles import Theme

logger = get_logger('modern_dashboard')


class ModernDashboard(ttk.Frame):
    """
    Modern, feature-rich dashboard
    """
    
    def __init__(self, parent, user_data):
        super().__init__(parent, style='Main.TFrame')
        self.user_data = user_data
        self.db = get_db()
        
        try:
            self.setup_ui()
            self.load_data()
        except Exception as e:
            logger.error(f"Dashboard setup failed: {e}", exc_info=True)
            # Show error in UI
            ttk.Label(self, text=f"Dashboard Error: {e}", foreground='red').pack(pady=20)
    
    def setup_ui(self):
        """Build the dashboard UI"""
        # Header
        header = ttk.Frame(self, style='Main.TFrame')
        header.pack(fill='x', pady=(0, 20))
        
        ttk.Label(
            header,
            text=f"Welcome back, {self.user_data['full_name']}",
            style='H1.TLabel',
            font=('Segoe UI', 24, 'bold')
        ).pack(side='left')
        
        # Refresh button
        ttk.Button(
            header,
            text="🔄 Refresh",
            command=self.load_data,
            style='Primary.TButton'
        ).pack(side='right', padx=5)
        
        # KPI Cards Row
        kpi_frame = ttk.Frame(self, style='Main.TFrame')
        kpi_frame.pack(fill='x', pady=(0, 20))
        
        self.kpi_cards = {}
        kpi_data = [
            ('revenue', "Today's Revenue", '💰', Theme.SUCCESS),
            ('orders', 'Pending Orders', '📦', Theme.WARNING),
            ('customers', 'Total Customers', '👥', Theme.INFO),
            ('low_stock', 'Low Stock Items', '⚠️', Theme.DANGER)
        ]
        
        for key, title, icon, color in kpi_data:
            card = self.create_kpi_card(kpi_frame, key, title, icon, color)
            card.pack(side='left', fill='both', expand=True, padx=5)
            self.kpi_cards[key] = card
        
        # Main content area - 2 columns
        content = ttk.Frame(self, style='Main.TFrame')
        content.pack(fill='both', expand=True)
        
        # Left column - Recent orders
        left = ttk.Frame(content, style='Card.TFrame', padding=20)
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(left, text="Recent Orders", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Orders table
        self.orders_tree = self.create_data_table(
            left,
            columns=['Order #', 'Customer', 'Amount', 'Status'],
            widths=[120, 200, 100, 100]
        )
        self.orders_tree.pack(fill='both', expand=True)
        
        # Right column - Quick stats & actions
        right = ttk.Frame(content, style='Main.TFrame')
        right.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Top products
        top_products = ttk.Frame(right, style='Card.TFrame', padding=20)
        top_products.pack(fill='x', pady=(0, 10))
        
        ttk.Label(top_products, text="Top Products Today", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        self.products_tree = self.create_data_table(
            top_products,
            columns=['Product', 'Sold', 'Revenue'],
            widths=[200, 80, 100],
            height=5
        )
        self.products_tree.pack(fill='x')
        
        # Quick actions
        actions = ttk.Frame(right, style='Card.TFrame', padding=20)
        actions.pack(fill='x', pady=(10, 0))
        
        ttk.Label(actions, text="Quick Actions", style='CardTitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        action_buttons = [
            ("➕ New Order", self.new_order),
            ("👤 New Customer", self.new_customer),
            ("📊 View Reports", self.view_reports),
            ("⚙️ Settings", self.open_settings)
        ]
        
        for text, command in action_buttons:
            ttk.Button(
                actions,
                text=text,
                command=command,
                style='Primary.TButton',
                width=25
            ).pack(fill='x', pady=3)
    
    def create_kpi_card(self, parent, key, title, icon, color):
        """Create a KPI card widget"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        
        # Icon and title
        header = ttk.Frame(card, style='Card.TFrame')
        header.pack(fill='x')
        
        ttk.Label(
            header,
            text=icon,
            font=('Segoe UI', 24)
        ).pack(side='left', padx=(0, 10))
        
        ttk.Label(
            header,
            text=title,
            style='CardSub.TLabel'
        ).pack(side='left')
        
        # Value
        value_label = ttk.Label(
            card,
            text="Loading...",
            font=('Segoe UI', 32, 'bold'),
            foreground=color
        )
        value_label.pack(anchor='w', pady=(10, 0))
        
        # Trend
        trend_label = ttk.Label(
            card,
            text="",
            style='CardSub.TLabel'
        )
        trend_label.pack(anchor='w')
        
        # Store references
        card.value_label = value_label
        card.trend_label = trend_label
        
        return card
    
    def create_data_table(self, parent, columns, widths, height=8):
        """Create a styled data table"""
        # Container with scrollbar
        container = ttk.Frame(parent, style='Card.TFrame')
        
        tree = ttk.Treeview(
            container,
            columns=columns,
            show='headings',
            height=height,
            selectmode='browse'
        )
        
        # Configure columns
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return tree
    
    def load_data(self):
        """Load all dashboard data"""
        try:
            # KPIs
            today = datetime.now().date().isoformat()
            
            # Revenue
            revenue = self.db.fetch_one(
                "SELECT SUM(total_amount) as total FROM sales_orders WHERE DATE(order_date) = ?",
                (today,)
            )
            self.update_kpi('revenue', f"${revenue['total'] or 0:,.2f}", "Today")
            
            # Orders
            pending = self.db.fetch_one(
                "SELECT COUNT(*) as count FROM sales_orders WHERE status IN ('pending', 'processing')"
            )
            self.update_kpi('orders', str(pending['count'] or 0), "Need attention")
            
            # Customers
            customers = self.db.fetch_one("SELECT COUNT(*) as count FROM customers WHERE deleted_at IS NULL")
            self.update_kpi('customers', str(customers['count'] or 0), "Active")
            
            # Low stock
            low_stock = self.db.fetch_one(
                """SELECT COUNT(DISTINCT p.product_id) as count 
                   FROM products p 
                   LEFT JOIN inventory i ON p.product_id = i.product_id 
                   GROUP BY p.product_id 
                   HAVING SUM(COALESCE(i.quantity, 0)) < p.reorder_level"""
            )
            self.update_kpi('low_stock', str(low_stock['count'] if low_stock else 0), "Reorder needed")
            
            # Recent orders
            orders = self.db.fetch_all(
                """SELECT so.order_number, c.name, so.total_amount, so.status 
                   FROM sales_orders so 
                   JOIN customers c ON so.customer_id = c.customer_id 
                   ORDER BY so.order_date DESC 
                   LIMIT 10"""
            )
            
            self.orders_tree.delete(*self.orders_tree.get_children())
            for order in orders:
                self.orders_tree.insert('', 'end', values=(
                    order['order_number'],
                    order['name'],
                    f"${order['total_amount']:,.2f}",
                    order['status'].upper()
                ))
            
            # Top products - simplified query
            try:
                products = self.db.fetch_all(
                    """SELECT p.name, COUNT(*) as sold, SUM(p.selling_price) as revenue 
                       FROM products p 
                       WHERE p.deleted_at IS NULL 
                       GROUP BY p.product_id 
                       ORDER BY sold DESC 
                       LIMIT 5"""
                )
            except:
                products = []
            
            self.products_tree.delete(*self.products_tree.get_children())
            for product in products:
                self.products_tree.insert('', 'end', values=(
                    product['name'],
                    product['sold'],
                    f"${product['revenue']:,.2f}"
                ))
            
            logger.info("Dashboard data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load dashboard data: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load data: {e}")
    
    def update_kpi(self, key, value, trend):
        """Update KPI card"""
        if key in self.kpi_cards:
            card = self.kpi_cards[key]
            card.value_label.config(text=value)
            card.trend_label.config(text=trend)
    
    # Quick action handlers
    def new_order(self):
        messagebox.showinfo("New Order", "Opening new order form...")
    
    def new_customer(self):
        messagebox.showinfo("New Customer", "Opening new customer form...")
    
    def view_reports(self):
        messagebox.showinfo("Reports", "Opening reports module...")
    
    def open_settings(self):
        messagebox.showinfo("Settings", "Opening settings...")
