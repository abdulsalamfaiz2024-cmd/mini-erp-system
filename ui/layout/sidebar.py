"""
Vertical Sidebar Navigation Component
Provides consistent navigation across all ERP modules
"""

import tkinter as tk
from tkinter import ttk
from ui.styles import Theme


class Sidebar(ttk.Frame):
    """
    Vertical sidebar with fixed navigation sections.
    Always visible, highlights active page.
    """
    
    # Navigation structure
    NAV_ITEMS = [
        {'id': 'dashboard', 'label': '📊 Dashboard'},
        {'type': 'separator'},
        {'id': 'sales_orders', 'label': '🛒 Sales Orders', 'section': 'Sales'},
        {'id': 'invoices', 'label': '🧾 Invoices', 'section': 'Sales'},
        {'id': 'returns', 'label': '↩️ Returns', 'section': 'Sales'},
        {'type': 'separator'},
        {'id': 'finance', 'label': '💰 Finance'},
        {'id': 'expenses', 'label': '💸 Expenses', 'section': 'Finance'},
        {'id': 'ledger', 'label': '📒 Ledger', 'section': 'Finance'},
        {'type': 'separator'},
        {'id': 'inventory', 'label': '📦 Inventory'},
        {'id': 'purchasing', 'label': '🛍️ Purchasing'},
        {'id': 'assets', 'label': '🏢 Assets'},
        {'type': 'separator'},
        {'id': 'accounting', 'label': '📚 Accounting'},
        {'type': 'separator'},
        {'id': 'employees', 'label': '👥 Employees'},
        {'id': 'customers', 'label': '🤝 Customers'},
        {'id': 'suppliers', 'label': '🚚 Suppliers'},
        {'type': 'separator'},
        {'id': 'reports', 'label': '📈 Reports'},
        {'id': 'settings', 'label': '⚙️ Settings'},
    ]
    
    def __init__(self, parent, on_navigate=None, user_data=None):
        super().__init__(parent, style='Sidebar.TFrame')
        self.on_navigate = on_navigate
        self.user_data = user_data
        self.active_page = 'dashboard'
        self.nav_buttons = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Build sidebar UI"""
        # Header - DARK
        header = tk.Frame(self, bg=Theme.PRIMARY, height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        ttk.Label(
            header, 
            text="Mini ERP", 
            font=('Segoe UI', 16, 'bold'),
            foreground='white',
            background=Theme.PRIMARY
        ).pack(pady=15)
        
        # Navigation container - DARK
        # Using Theme.PRIMARY instead of BG_WHITE to restore dark look
        nav_container = tk.Frame(self, bg=Theme.PRIMARY)
        nav_container.pack(fill='both', expand=True, side='top')
        
        # Build navigation items
        for item in self.NAV_ITEMS:
            if item.get('type') == 'separator':
                # Dark separator
                sep = tk.Frame(nav_container, bg='#34495e', height=1)
                sep.pack(fill='x', padx=10, pady=5)
            else:
                self._create_nav_button(nav_container, item)
        
        # Footer (user info) - DARK
        footer = tk.Frame(self, bg=Theme.PRIMARY, height=50)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        if self.user_data:
            user_label = ttk.Label(
                footer,
                text=f"👤 {self.user_data.get('full_name', 'User')}",
                font=('Segoe UI', 9),
                background=Theme.PRIMARY,
                foreground='#aec4da'
            )
            user_label.pack(pady=10, padx=10)
    
    def _create_nav_button(self, parent, item):
        """Create a navigation button"""
        # Dark background
        btn_frame = tk.Frame(parent, bg=Theme.PRIMARY)
        btn_frame.pack(fill='x', padx=5, pady=2)
        
        # Indent if part of a section
        padx = (20, 5) if item.get('section') else (5, 5)
        
        # Use label as button
        btn = tk.Label(
            btn_frame,
            text=f"  {item['label']}",  # Label already includes icon
            font=('Segoe UI', 10),
            fg='#aec4da',        # Light blue-grey text
            bg=Theme.PRIMARY,    # Dark background
            anchor='w',
            padx=10,
            pady=8,
            cursor='hand2'
        )
        btn.pack(fill='x')
        
        # Bind click
        btn.bind('<Button-1>', lambda e, page=item['id']: self.on_item_click(page))
        
        # Store for state updates
        self.nav_buttons[item['id']] = btn
        
    def on_item_click(self, page_id):
        if self.on_navigate:
            self.update_active_state(page_id)
            self.on_navigate(page_id)
            
    def update_active_state(self, active_id):
        """Highlight active button"""
        self.active_page = active_id
        
        for page_id, btn in self.nav_buttons.items():
            if page_id == active_id:
                btn.configure(
                    bg='#1A252F',   # Darker active background (Theme.PRIMARY_DARK ish)
                    fg='white',
                    font=('Segoe UI', 10, 'bold')
                )
            else:
                btn.configure(
                    bg=Theme.PRIMARY,
                    fg='#aec4da',
                    font=('Segoe UI', 10)
                )
