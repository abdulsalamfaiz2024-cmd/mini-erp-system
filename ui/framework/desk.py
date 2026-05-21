"""
Professional ERPNext-Style Desk Application
Main application window with sidebar navigation, workspace, and content area.
All buttons connected to backend controllers.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.framework.desk_styles import apply_desk_theme, Theme, create_card
from ui.framework.list_view import ListView
from ui.framework.form_view import FormView
import core.frappe as frappe
from core.database import db, get_table_name


class Desk(tk.Tk):
    """
    Main Desk Application - Professional ERPNext-style interface.
    Navy Blue + Orange Theme.
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Mini ERPNext - Sales System")
        self.geometry("1400x850")
        self.minsize(1200, 700)
        
        # Apply professional theme
        apply_desk_theme(self)
        
        # Navigation state
        self.current_view = None
        
        self.setup_ui()
        self.show_home()
    
    def setup_ui(self):
        """Build the main UI structure"""
        # Main container
        main_container = ttk.Frame(self, style="Desk.TFrame")
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = self.create_sidebar(main_container)
        self.sidebar.pack(side="left", fill="y")
        
        # Right side container
        right_container = ttk.Frame(main_container, style="Desk.TFrame")
        right_container.pack(side="left", fill="both", expand=True)
        
        # Top bar
        self.topbar = self.create_topbar(right_container)
        self.topbar.pack(fill="x")
        
        # Main viewport with padding
        viewport_container = ttk.Frame(right_container, style="Desk.TFrame")
        viewport_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.viewport = ttk.Frame(viewport_container, style="Content.TFrame")
        self.viewport.pack(fill="both", expand=True)
    
    def create_sidebar(self, parent):
        """Create the sidebar with module navigation"""
        sidebar = tk.Frame(parent, bg=Theme.BG_SIDEBAR, width=240)
        sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(sidebar, bg=Theme.BG_SIDEBAR)
        logo_frame.pack(fill="x", pady=20, padx=15)
        
        tk.Label(logo_frame, text="Mini ERPNext", 
                 font=(Theme.FONT_FAMILY, 16, "bold"),
                 fg=Theme.TEXT_LIGHT, bg=Theme.BG_SIDEBAR).pack(anchor="w")
        
        tk.Label(logo_frame, text="Sales Management System", 
                 font=(Theme.FONT_FAMILY, 9),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_SIDEBAR).pack(anchor="w")
        
        # Separator
        tk.Frame(sidebar, bg=Theme.PRIMARY_LIGHT, height=1).pack(fill="x", padx=15, pady=10)
        
        # Navigation sections
        nav_sections = [
            ("MAIN", [
                ("🏠  Home", self.show_home),
            ]),
            ("MODULES", [
                ("📦  Selling", lambda: self.show_module("Selling")),
                ("🛒  Buying", lambda: self.show_module("Buying")),
                ("📊  Stock", lambda: self.show_module("Stock")),
                ("💰  Accounts", lambda: self.show_module("Accounts")),
            ]),
            ("MASTERS", [
                ("👥  Customers", lambda: self.open_list("Customer")),
                ("🏭  Suppliers", lambda: self.open_list("Supplier")),
                ("📋  Items", lambda: self.open_list("Item")),
                ("🏢  Warehouses", lambda: self.open_list("Warehouse")),
            ]),
            ("TRANSACTIONS", [
                ("📝  Sales Orders", lambda: self.open_list("Sales Order")),
                ("📦  Stock Ledger", lambda: self.open_list("Stock Ledger Entry")),
                ("📒  GL Entries", lambda: self.open_list("GL Entry")),
            ]),
        ]
        
        for section_title, items in nav_sections:
            # Section header
            tk.Label(sidebar, text=section_title,
                     font=(Theme.FONT_FAMILY, 9, "bold"),
                     fg=Theme.TEXT_MUTED, bg=Theme.BG_SIDEBAR).pack(anchor="w", padx=15, pady=(15, 5))
            
            for label, command in items:
                btn = tk.Button(sidebar, text=label,
                               font=(Theme.FONT_FAMILY, 11),
                               fg=Theme.TEXT_LIGHT, bg=Theme.BG_SIDEBAR,
                               activeforeground=Theme.TEXT_LIGHT,
                               activebackground=Theme.PRIMARY_LIGHT,
                               bd=0, padx=15, pady=8,
                               anchor="w", cursor="hand2",
                               command=command)
                btn.pack(fill="x")
                
                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=Theme.PRIMARY_LIGHT))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=Theme.BG_SIDEBAR))
        
        return sidebar
    
    def create_topbar(self, parent):
        """Create the top bar with breadcrumbs and actions"""
        topbar = tk.Frame(parent, bg=Theme.BG_WHITE, height=60)
        topbar.pack_propagate(False)
        
        # Left side - Breadcrumbs
        left_frame = tk.Frame(topbar, bg=Theme.BG_WHITE)
        left_frame.pack(side="left", fill="y", padx=20)
        
        self.breadcrumb = tk.Label(left_frame, text="Home",
                                   font=(Theme.FONT_FAMILY, 12),
                                   fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE)
        self.breadcrumb.pack(side="left", pady=18)
        
        # Right side - Quick actions
        right_frame = tk.Frame(topbar, bg=Theme.BG_WHITE)
        right_frame.pack(side="right", fill="y", padx=20)
        
        # Quick Create button (Accent color)
        quick_btn = tk.Menubutton(right_frame, text="+ Quick Create",
                                  font=(Theme.FONT_FAMILY, 10, "bold"),
                                  fg=Theme.TEXT_DARK, bg=Theme.ACCENT,
                                  activeforeground=Theme.TEXT_DARK,
                                  activebackground=Theme.ACCENT_DARK,
                                  bd=0, padx=15, pady=8,
                                  cursor="hand2", relief="flat")
        quick_btn.pack(side="right", pady=12)
        
        # Quick create menu
        quick_menu = tk.Menu(quick_btn, tearoff=0,
                            font=(Theme.FONT_FAMILY, 10),
                            bg=Theme.BG_WHITE, fg=Theme.TEXT_DARK)
        quick_menu.add_command(label="📝 Sales Order", command=lambda: self.open_form("Sales Order"))
        quick_menu.add_command(label="👤 Customer", command=lambda: self.open_form("Customer"))
        quick_menu.add_command(label="📦 Item", command=lambda: self.open_form("Item"))
        quick_menu.add_separator()
        quick_menu.add_command(label="🏭 Supplier", command=lambda: self.open_form("Supplier"))
        quick_menu.add_command(label="🏢 Warehouse", command=lambda: self.open_form("Warehouse"))
        quick_btn["menu"] = quick_menu
        
        # Separator line at bottom
        tk.Frame(topbar, bg=Theme.BORDER, height=1).pack(side="bottom", fill="x")
        
        return topbar
    
    def clear_viewport(self):
        """Clear the main viewport"""
        for widget in self.viewport.winfo_children():
            widget.destroy()
    
    def set_breadcrumb(self, *parts):
        """Update breadcrumb with path"""
        text = " > ".join(parts)
        self.breadcrumb.config(text=text)
    
    def show_home(self):
        """Show home dashboard"""
        self.clear_viewport()
        self.set_breadcrumb("Home")
        
        # Main container with padding
        container = tk.Frame(self.viewport, bg=Theme.BG_WHITE)
        container.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Welcome header
        tk.Label(container, text="Welcome to Mini ERPNext",
                 font=(Theme.FONT_FAMILY, 24, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(anchor="w")
        
        tk.Label(container, text="Your complete sales management system - All features connected to backend",
                 font=(Theme.FONT_FAMILY, 11),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_WHITE).pack(anchor="w", pady=(5, 25))
        
        # Stats row
        stats_frame = tk.Frame(container, bg=Theme.BG_WHITE)
        stats_frame.pack(fill="x", pady=10)
        
        stats = [
            ("Customers", "Customer", Theme.PRIMARY),
            ("Items", "Item", Theme.SUCCESS),
            ("Sales Orders", "Sales Order", Theme.ACCENT),
            ("Suppliers", "Supplier", Theme.INFO),
        ]
        
        for i, (label, doctype, color) in enumerate(stats):
            self.create_stat_card(stats_frame, label, doctype, color, i)
        
        # Quick Actions section
        tk.Label(container, text="Quick Actions",
                 font=(Theme.FONT_FAMILY, 16, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(anchor="w", pady=(30, 15))
        
        actions_frame = tk.Frame(container, bg=Theme.BG_WHITE)
        actions_frame.pack(fill="x")
        
        actions = [
            ("+ New Sales Order", "Sales Order", Theme.PRIMARY),
            ("+ New Customer", "Customer", Theme.SUCCESS),
            ("+ New Item", "Item", Theme.ACCENT),
        ]
        
        for i, (label, doctype, color) in enumerate(actions):
            btn = tk.Button(actions_frame, text=label,
                           font=(Theme.FONT_FAMILY, 11, "bold"),
                           fg=Theme.TEXT_LIGHT, bg=color,
                           activeforeground=Theme.TEXT_LIGHT,
                           activebackground=color,
                           bd=0, padx=25, pady=12,
                           cursor="hand2",
                           command=lambda dt=doctype: self.open_form(dt))
            btn.grid(row=0, column=i, padx=(0, 15), sticky="w")
        
        # Recent Activity section
        tk.Label(container, text="Recent Sales Orders",
                 font=(Theme.FONT_FAMILY, 16, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(anchor="w", pady=(30, 15))
        
        self.show_recent_orders(container)
    
    def create_stat_card(self, parent, title, doctype, color, col):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=Theme.BG_WHITE, bd=1, relief="solid",
                       highlightbackground=Theme.BORDER, highlightthickness=1)
        card.grid(row=0, column=col, padx=(0, 15), pady=5, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        
        inner = tk.Frame(card, bg=Theme.BG_WHITE)
        inner.pack(padx=20, pady=20)
        
        # Get count from database
        try:
            table = get_table_name(doctype)
            result = db.sql(f"SELECT COUNT(*) as count FROM {table}", as_dict=True)
            count = result[0]['count'] if result else 0
        except:
            count = 0
        
        # Count
        tk.Label(inner, text=str(count),
                 font=(Theme.FONT_FAMILY, 32, "bold"),
                 fg=color, bg=Theme.BG_WHITE).pack()
        
        # Title
        tk.Label(inner, text=title,
                 font=(Theme.FONT_FAMILY, 11),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_WHITE).pack()
        
        # Make clickable
        for widget in [card, inner] + list(inner.winfo_children()):
            widget.configure(cursor="hand2")
            widget.bind("<Button-1>", lambda e, dt=doctype: self.open_list(dt))
    
    def show_recent_orders(self, parent):
        """Show recent sales orders table"""
        try:
            table = get_table_name("Sales Order")
            orders = db.sql(f"SELECT name, customer, docstatus, grand_total FROM {table} ORDER BY name DESC LIMIT 5", as_dict=True)
            
            if orders:
                # Table frame
                table_frame = tk.Frame(parent, bg=Theme.BG_WHITE, bd=1, relief="solid",
                                      highlightbackground=Theme.BORDER, highlightthickness=1)
                table_frame.pack(fill="x")
                
                # Header
                header = tk.Frame(table_frame, bg=Theme.BG_LIGHT)
                header.pack(fill="x")
                
                for i, col in enumerate(["Order ID", "Customer", "Status", "Total", "Action"]):
                    tk.Label(header, text=col,
                            font=(Theme.FONT_FAMILY, 10, "bold"),
                            fg=Theme.TEXT_DARK, bg=Theme.BG_LIGHT,
                            width=20 if i < 4 else 15).grid(row=0, column=i, padx=10, pady=10, sticky="w")
                
                # Rows
                for order in orders:
                    row_frame = tk.Frame(table_frame, bg=Theme.BG_WHITE)
                    row_frame.pack(fill="x")
                    
                    # Add separator
                    tk.Frame(row_frame, bg=Theme.BORDER, height=1).pack(fill="x")
                    
                    row_content = tk.Frame(row_frame, bg=Theme.BG_WHITE)
                    row_content.pack(fill="x")
                    
                    status = "Draft" if order.get('docstatus', 0) == 0 else "Submitted" if order.get('docstatus') == 1 else "Cancelled"
                    status_color = Theme.TEXT_MUTED if status == "Draft" else Theme.SUCCESS if status == "Submitted" else Theme.DANGER
                    
                    values = [
                        order.get('name', ''),
                        order.get('customer', ''),
                        status,
                        f"${order.get('grand_total', 0):.2f}" if order.get('grand_total') else "$0.00"
                    ]
                    
                    for i, val in enumerate(values):
                        fg = status_color if i == 2 else Theme.TEXT_DARK
                        tk.Label(row_content, text=str(val),
                                font=(Theme.FONT_FAMILY, 10),
                                fg=fg, bg=Theme.BG_WHITE,
                                width=20).grid(row=0, column=i, padx=10, pady=12, sticky="w")
                    
                    # Open button
                    open_btn = tk.Button(row_content, text="Open",
                                        font=(Theme.FONT_FAMILY, 9),
                                        fg=Theme.PRIMARY, bg=Theme.BG_WHITE,
                                        bd=1, padx=10, pady=3,
                                        cursor="hand2",
                                        command=lambda n=order.get('name'): self.open_form("Sales Order", n))
                    open_btn.grid(row=0, column=4, padx=10, pady=8)
            else:
                tk.Label(parent, text="No sales orders yet. Create your first one!",
                        font=(Theme.FONT_FAMILY, 11),
                        fg=Theme.TEXT_MUTED, bg=Theme.BG_WHITE).pack(anchor="w", pady=10)
                
        except Exception as e:
            tk.Label(parent, text=f"Could not load orders: {e}",
                    font=(Theme.FONT_FAMILY, 11),
                    fg=Theme.DANGER, bg=Theme.BG_WHITE).pack(anchor="w", pady=10)
    
    def show_module(self, module_name):
        """Show module workspace"""
        self.clear_viewport()
        self.set_breadcrumb("Home", module_name)
        
        container = tk.Frame(self.viewport, bg=Theme.BG_WHITE)
        container.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Module header
        tk.Label(container, text=f"{module_name} Module",
                 font=(Theme.FONT_FAMILY, 24, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(anchor="w")
        
        tk.Label(container, text=f"Manage all {module_name.lower()} operations",
                 font=(Theme.FONT_FAMILY, 11),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_WHITE).pack(anchor="w", pady=(5, 25))
        
        # Module-specific shortcuts
        shortcuts = {
            "Selling": [
                ("Sales Orders", "Sales Order", "Create and manage sales orders"),
                ("Customers", "Customer", "Manage customer information"),
            ],
            "Buying": [
                ("Suppliers", "Supplier", "Manage supplier information"),
            ],
            "Stock": [
                ("Items", "Item", "Manage inventory items"),
                ("Warehouses", "Warehouse", "Manage warehouse locations"),
                ("Stock Ledger", "Stock Ledger Entry", "View stock movements"),
                ("Bins", "Bin", "Real-time stock levels"),
            ],
            "Accounts": [
                ("Chart of Accounts", "Account", "Manage accounts"),
                ("GL Entries", "GL Entry", "General ledger entries"),
            ],
        }
        
        cards_frame = tk.Frame(container, bg=Theme.BG_WHITE)
        cards_frame.pack(fill="x", pady=20)
        
        for i, (label, doctype, desc) in enumerate(shortcuts.get(module_name, [])):
            self.create_module_card(cards_frame, label, doctype, desc, i)
    
    def create_module_card(self, parent, title, doctype, description, col):
        """Create a module shortcut card"""
        card = tk.Frame(parent, bg=Theme.BG_WHITE, bd=1, relief="solid",
                       highlightbackground=Theme.BORDER, highlightthickness=1)
        card.grid(row=col // 3, column=col % 3, padx=(0, 15), pady=10, sticky="nsew")
        parent.columnconfigure(col % 3, weight=1)
        
        inner = tk.Frame(card, bg=Theme.BG_WHITE)
        inner.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        tk.Label(inner, text=title,
                 font=(Theme.FONT_FAMILY, 14, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(anchor="w")
        
        # Description
        tk.Label(inner, text=description,
                 font=(Theme.FONT_FAMILY, 10),
                 fg=Theme.TEXT_MUTED, bg=Theme.BG_WHITE).pack(anchor="w", pady=(5, 15))
        
        # Buttons
        btn_frame = tk.Frame(inner, bg=Theme.BG_WHITE)
        btn_frame.pack(anchor="w")
        
        # View List button
        list_btn = tk.Button(btn_frame, text="View List",
                            font=(Theme.FONT_FAMILY, 10),
                            fg=Theme.PRIMARY, bg=Theme.BG_WHITE,
                            bd=1, padx=12, pady=5,
                            cursor="hand2",
                            command=lambda dt=doctype: self.open_list(dt))
        list_btn.pack(side="left", padx=(0, 10))
        
        # New button
        new_btn = tk.Button(btn_frame, text="+ New",
                           font=(Theme.FONT_FAMILY, 10, "bold"),
                           fg=Theme.TEXT_LIGHT, bg=Theme.PRIMARY,
                           bd=0, padx=12, pady=5,
                           cursor="hand2",
                           command=lambda dt=doctype: self.open_form(dt))
        new_btn.pack(side="left")
    
    def open_list(self, doctype):
        """Open list view for a doctype - CONNECTED TO BACKEND"""
        self.clear_viewport()
        self.set_breadcrumb("Home", doctype, "List")
        
        list_view = ListView(
            self.viewport,
            doctype,
            on_edit=self.open_form,
            on_create=lambda dt: self.open_form(dt),
            on_back=self.show_home
        )
        list_view.pack(fill="both", expand=True)
    
    def open_form(self, doctype, name=None):
        """Open form view for a doctype - CONNECTED TO BACKEND CONTROLLERS"""
        self.clear_viewport()
        title = name if name else "New"
        self.set_breadcrumb("Home", doctype, title)
        
        form_view = FormView(
            self.viewport,
            doctype,
            name=name,
            on_back=lambda: self.open_list(doctype)
        )
        form_view.pack(fill="both", expand=True)


def main():
    """Run the Desk application"""
    from core.schema import sync_all_doctypes
    
    print("Initializing database schema...")
    sync_all_doctypes()
    
    print("Starting Mini ERPNext Desk...")
    app = Desk()
    app.mainloop()


if __name__ == "__main__":
    main()
