"""
Global Search System for Mini-ERP
Provides Ctrl+K quick search across all entities
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.database import get_db
from core.logger import get_logger
from core.cache import cached, LRUCache
from ui.styles import Theme

logger = get_logger('global_search')

# Search results cache
_search_cache = LRUCache(max_size=100, default_ttl=60)


class GlobalSearchDialog(tk.Toplevel):
    """
    Global search dialog (Ctrl+K)
    Searches across customers, products, orders, suppliers
    """
    
    def __init__(self, parent, on_select_callback=None):
        super().__init__(parent)
        
        self.on_select_callback = on_select_callback
        self.search_results = []
        
        self.setup_window()
        self.setup_ui()
        
        # Focus on search box
        self.search_entry.focus_set()
        
        # Bind Escape to close
        self.bind('<Escape>', lambda e: self.destroy())
    
    def setup_window(self):
        """Configure window"""
        self.title("Quick Search (Ctrl+K)")
        self.geometry("700x500")
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"700x500+{x}+{y}")
        
        # Modal
        self.transient(self.master)
        self.grab_set()
        
        # Apply theme
        Theme.apply_styles(self)
    
    def setup_ui(self):
        """Setup UI components"""
        # Main container
        container = ttk.Frame(self, style='Main.TFrame', padding=20)
        container.pack(fill='both', expand=True)
        
        # Search box
        search_frame = ttk.Frame(container, style='Card.TFrame')
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(
            search_frame,
            text="🔍 Search:",
            style='H2.TLabel',
            font=('Arial', 11)
        ).pack(side='left', padx=10, pady=10)
        
        self.search_entry = ttk.Entry(search_frame, font=('Arial', 11))
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10), pady=10)
        
        # Bind search on key release
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<Return>', self.on_select)
        self.search_entry.bind('<Down>', lambda e: self.results_tree.focus_set())
        
        # Filter buttons
        filter_frame = ttk.Frame(container, style='Main.TFrame')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:", style='Body.TLabel').pack(side='left', padx=(0, 10))
        
        self.filter_var = tk.StringVar(value='all')
        filters = [
            ('All', 'all'),
            ('Customers', 'customers'),
            ('Products', 'products'),
            ('Orders', 'orders'),
            ('Suppliers', 'suppliers')
        ]
        
        for label, value in filters:
            ttk.Radiobutton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=value,
                command=self.on_filter_change
            ).pack(side='left', padx=5)
        
        # Results area
        results_frame = ttk.Frame(container, style='Card.TFrame')
        results_frame.pack(fill='both', expand=True)
        
        # Treeview for results
        columns = ('type', 'id', 'name', 'details')
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show='headings',
            selectmode='browse',
            height=15
        )
        
        # Configure columns
        self.results_tree.heading('type', text='Type')
        self.results_tree.heading('id', text='ID')
        self.results_tree.heading('name', text='Name')
        self.results_tree.heading('details', text='Details')
        
        self.results_tree.column('type', width=100)
        self.results_tree.column('id', width=120)
        self.results_tree.column('name', width=200)
        self.results_tree.column('details', width=250)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection
        self.results_tree.bind('<Double-Button-1>', self.on_select)
        self.results_tree.bind('<Return>', self.on_select)
        
        # Status bar
        self.status_label = ttk.Label(
            container,
            text="Type to search...",
            style='Body.TLabel',
            foreground='#7f8c8d'
        )
        self.status_label.pack(fill='x', pady=(10, 0))
    
    def on_search_change(self, event=None):
        """Handle search text change"""
        query = self.search_entry.get().strip()
        
        if len(query) < 2:
            self.clear_results()
            self.status_label.config(text="Type at least 2 characters to search...")
            return
        
        # Perform search
        self.perform_search(query)
    
    def on_filter_change(self):
        """Handle filter change"""
        query = self.search_entry.get().strip()
        if len(query) >= 2:
            self.perform_search(query)
    
    def perform_search(self, query: str):
        """
        Search across all entities
        
        Args:
            query: Search query string
        """
        try:
            filter_type = self.filter_var.get()
            
            # Check cache
            cache_key = f"{query}:{filter_type}"
            cached_results = _search_cache.get(cache_key)
            if cached_results:
                self.display_results(cached_results)
                return
            
            db = get_db()
            results = []
            
            # Search customers
            if filter_type in ('all', 'customers'):
                customers = db.fetch_all(
                    """SELECT customer_id, name, email, phone 
                       FROM customers 
                       WHERE (name LIKE ? OR customer_id LIKE ? OR email LIKE ? OR phone LIKE ?)
                       AND deleted_at IS NULL
                       LIMIT 20""",
                    (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%')
                )
                for c in customers:
                    results.append({
                        'type': 'Customer',
                        'id': c['customer_id'],
                        'name': c['name'],
                        'details': f"{c['email'] or ''} | {c['phone'] or ''}",
                        'entity_type': 'customer',
                        'data': dict(c)
                    })
            
            # Search products
            if filter_type in ('all', 'products'):
                products = db.fetch_all(
                    """SELECT product_id, name, category, selling_price 
                       FROM products 
                       WHERE (name LIKE ? OR product_id LIKE ? OR category LIKE ?)
                       AND deleted_at IS NULL
                       LIMIT 20""",
                    (f'%{query}%', f'%{query}%', f'%{query}%')
                )
                for p in products:
                    results.append({
                        'type': 'Product',
                        'id': p['product_id'],
                        'name': p['name'],
                        'details': f"{p['category'] or 'N/A'} | Price: {p['selling_price']}",
                        'entity_type': 'product',
                        'data': dict(p)
                    })
            
            # Search sales orders
            if filter_type in ('all', 'orders'):
                orders = db.fetch_all(
                    """SELECT so.order_number, so.order_date, so.total_amount, so.status, c.name as customer_name
                       FROM sales_orders so
                       JOIN customers c ON so.customer_id = c.customer_id
                       WHERE (so.order_number LIKE ? OR c.name LIKE ?)
                       AND so.deleted_at IS NULL
                       LIMIT 20""",
                    (f'%{query}%', f'%{query}%')
                )
                for o in orders:
                    results.append({
                        'type': 'Order',
                        'id': o['order_number'],
                        'name': o['customer_name'],
                        'details': f"{o['order_date']} | {o['total_amount']} | {o['status']}",
                        'entity_type': 'order',
                        'data': dict(o)
                    })
            
            # Search suppliers
            if filter_type in ('all', 'suppliers'):
                suppliers = db.fetch_all(
                    """SELECT supplier_id, name, email, phone 
                       FROM suppliers 
                       WHERE (name LIKE ? OR supplier_id LIKE ? OR email LIKE ?)
                       AND deleted_at IS NULL
                       LIMIT 20""",
                    (f'%{query}%', f'%{query}%', f'%{query}%')
                )
                for s in suppliers:
                    results.append({
                        'type': 'Supplier',
                        'id': s['supplier_id'],
                        'name': s['name'],
                        'details': f"{s['email'] or ''} | {s['phone'] or ''}",
                        'entity_type': 'supplier',
                        'data': dict(s)
                    })
            
            # Cache results
            _search_cache.set(cache_key, results)
            
            # Display
            self.display_results(results)
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            self.status_label.config(text=f"Search error: {e}")
    
    def display_results(self, results: List[Dict]):
        """Display search results"""
        self.search_results = results
        
        # Clear existing
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add results
        for result in results:
            self.results_tree.insert('', 'end', values=(
                result['type'],
                result['id'],
                result['name'],
                result['details']
            ))
        
        # Update status
        count = len(results)
        self.status_label.config(text=f"Found {count} result{'s' if count != 1 else ''}")
        
        # Select first result
        if results:
            first_item = self.results_tree.get_children()[0]
            self.results_tree.selection_set(first_item)
            self.results_tree.focus(first_item)
    
    def clear_results(self):
        """Clear results"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.search_results = []
    
    def on_select(self, event=None):
        """Handle result selection"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        # Get selected index
        item = selection[0]
        index = self.results_tree.index(item)
        
        if index < len(self.search_results):
            result = self.search_results[index]
            
            # Call callback
            if self.on_select_callback:
                self.on_select_callback(result)
            
            # Close dialog
            self.destroy()


def show_global_search(parent, on_select_callback=None):
    """
    Show global search dialog
    
    Args:
        parent: Parent window
        on_select_callback: Callback function(result_dict) when item selected
    """
    dialog = GlobalSearchDialog(parent, on_select_callback)
    return dialog


# Keyboard shortcut helper
def bind_global_search(root, on_select_callback=None):
    """
    Bind Ctrl+K to show global search
    
    Args:
        root: Root window
        on_select_callback: Callback for selection
    """
    def show_search(event=None):
        show_global_search(root, on_select_callback)
    
    root.bind('<Control-k>', show_search)
    root.bind('<Control-K>', show_search)
    
    logger.info("Global search bound to Ctrl+K")
