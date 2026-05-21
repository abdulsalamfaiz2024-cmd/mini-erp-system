"""
Advanced Search & Filter System
Powerful search across all entities with filters
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
from datetime import datetime

from core.database import get_db
from ui.styles import Theme


class AdvancedSearchWindow(tk.Toplevel):
    """Advanced search with filters and export"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Advanced Search")
        self.geometry("900x600")
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 450
        y = (self.winfo_screenheight() // 2) - 300
        self.geometry(f"900x600+{x}+{y}")
        
        self.db = get_db()
        self.setup_ui()
    
    def setup_ui(self):
        """Build search interface"""
        # Search bar
        search_frame = ttk.Frame(self, padding=20)
        search_frame.pack(fill='x')
        
        ttk.Label(search_frame, text="🔍 Search:", font=('Segoe UI', 12, 'bold')).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11), width=50)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self.perform_search())
        
        ttk.Button(search_frame, text="Search", command=self.perform_search, style='Primary.TButton').pack(side='left')
        
        # Filters
        filter_frame = ttk.LabelFrame(self, text="Filters", padding=15)
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # Entity type filter
        ttk.Label(filter_frame, text="Search in:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.entity_var = tk.StringVar(value='all')
        entities = ['All', 'Customers', 'Products', 'Orders', 'Suppliers', 'Invoices']
        entity_combo = ttk.Combobox(filter_frame, textvariable=self.entity_var, values=entities, state='readonly', width=15)
        entity_combo.grid(row=0, column=1, sticky='w')
        
        # Date range
        ttk.Label(filter_frame, text="Date from:").grid(row=0, column=2, sticky='w', padx=(20, 10))
        self.date_from = ttk.Entry(filter_frame, width=12)
        self.date_from.grid(row=0, column=3, sticky='w')
        self.date_from.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Label(filter_frame, text="to:").grid(row=0, column=4, sticky='w', padx=(10, 10))
        self.date_to = ttk.Entry(filter_frame, width=12)
        self.date_to.grid(row=0, column=5, sticky='w')
        self.date_to.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Results
        results_frame = ttk.Frame(self, padding=(20, 0, 20, 20))
        results_frame.pack(fill='both', expand=True)
        
        ttk.Label(results_frame, text="Results", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Results table
        columns = ('Type', 'ID', 'Name', 'Details', 'Date')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status
        self.status_label = ttk.Label(self, text="Enter search term and press Enter", foreground='gray')
        self.status_label.pack(fill='x', padx=20, pady=(0, 10))
        
        # Bind double-click
        self.results_tree.bind('<Double-Button-1>', self.on_result_select)
    
    def perform_search(self):
        """Execute search"""
        query = self.search_var.get().strip()
        if len(query) < 2:
            self.status_label.config(text="Please enter at least 2 characters")
            return
        
        entity = self.entity_var.get().lower()
        results = []
        
        try:
            # Search customers
            if entity in ('all', 'customers'):
                customers = self.db.fetch_all(
                    """SELECT customer_id, name, email, phone, created_at 
                       FROM customers 
                       WHERE (name LIKE ? OR customer_id LIKE ? OR email LIKE ?) 
                       AND deleted_at IS NULL 
                       LIMIT 50""",
                    (f'%{query}%', f'%{query}%', f'%{query}%')
                )
                for c in customers:
                    results.append(('Customer', c['customer_id'], c['name'], 
                                  f"{c['email']} | {c['phone']}", c['created_at']))
            
            # Search products
            if entity in ('all', 'products'):
                products = self.db.fetch_all(
                    """SELECT product_id, name, category, selling_price, created_at 
                       FROM products 
                       WHERE (name LIKE ? OR product_id LIKE ?) 
                       AND deleted_at IS NULL 
                       LIMIT 50""",
                    (f'%{query}%', f'%{query}%')
                )
                for p in products:
                    results.append(('Product', p['product_id'], p['name'], 
                                  f"{p['category']} | ${p['selling_price']}", p['created_at']))
            
            # Search orders
            if entity in ('all', 'orders'):
                orders = self.db.fetch_all(
                    """SELECT so.order_number, c.name, so.total_amount, so.status, so.order_date 
                       FROM sales_orders so 
                       JOIN customers c ON so.customer_id = c.customer_id 
                       WHERE (so.order_number LIKE ? OR c.name LIKE ?) 
                       LIMIT 50""",
                    (f'%{query}%', f'%{query}%')
                )
                for o in orders:
                    results.append(('Order', o['order_number'], o['name'], 
                                  f"${o['total_amount']} | {o['status']}", o['order_date']))
            
            # Display results
            self.results_tree.delete(*self.results_tree.get_children())
            for result in results:
                self.results_tree.insert('', 'end', values=result)
            
            self.status_label.config(text=f"Found {len(results)} results")
            
        except Exception as e:
            self.status_label.config(text=f"Search error: {e}")
    
    def on_result_select(self, event):
        """Handle result selection"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            values = item['values']
            print(f"Selected: {values[0]} - {values[1]}")
