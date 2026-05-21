"""
Professional ERPNext-Style Desk Application
Main application window with sidebar navigation, workspace, and content area.
"""
import tkinter as tk
from tkinter import ttk
from ui.framework.desk_styles import apply_desk_theme
from ui.framework.list_view import ListView
from ui.framework.form_view import FormView


class Desk(tk.Tk):
    """
    Main Desk Application - ERPNext-style interface.
    Features:
    - Sidebar with module navigation
    - Workspace area
    - Breadcrumb navigation
    - Quick actions
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Mini ERPNext - Sales System")
        self.geometry("1400x800")
        self.minsize(1200, 700)
        
        # Apply theme
        apply_desk_theme(self)
        
        # Navigation state
        self.history = []
        
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
        
        # Content area
        content_area = ttk.Frame(main_container, style="Desk.TFrame")
        content_area.pack(side="left", fill="both", expand=True)
        
        # Top bar
        self.topbar = self.create_topbar(content_area)
        self.topbar.pack(fill="x")
        
        # Main viewport
        self.viewport = ttk.Frame(content_area, style="Content.TFrame")
        self.viewport.pack(fill="both", expand=True)
    
    def create_sidebar(self, parent):
        """Create the sidebar with module navigation"""
        sidebar = ttk.Frame(parent, style="Sidebar.TFrame", width=220)
        sidebar.pack_propagate(False)
        
        # Logo
        logo_frame = ttk.Frame(sidebar, style="Sidebar.TFrame")
        logo_frame.pack(fill="x", pady=15)
        
        ttk.Label(logo_frame, text="Mini ERPNext", 
                  font=("Segoe UI", 14, "bold"),
                  foreground="white", background="#1a1a2e").pack(padx=15)
        
        ttk.Label(logo_frame, text="Sales System", 
                  font=("Segoe UI", 9),
                  foreground="#888", background="#1a1a2e").pack(padx=15)
        
        # Separator
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)
        
        # Navigation items
        nav_items = [
            ("Home", "home", self.show_home),
            ("---", None, None),
            ("MODULES", None, None),
            ("Selling", "selling", lambda: self.show_module("Selling")),
            ("Buying", "buying", lambda: self.show_module("Buying")),
            ("Stock", "stock", lambda: self.show_module("Stock")),
            ("Accounts", "accounts", lambda: self.show_module("Accounts")),
            ("---", None, None),
            ("MASTERS", None, None),
            ("Customers", "customer", lambda: self.open_list("Customer")),
            ("Suppliers", "supplier", lambda: self.open_list("Supplier")),
            ("Items", "item", lambda: self.open_list("Item")),
            ("Warehouses", "warehouse", lambda: self.open_list("Warehouse")),
            ("---", None, None),
            ("REPORTS", None, None),
            ("Stock Ledger", "stock_ledger", lambda: self.open_list("Stock Ledger Entry")),
            ("GL Entries", "gl_entry", lambda: self.open_list("GL Entry")),
        ]
        
        for item in nav_items:
            label, key, action = item
            
            if label == "---":
                ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=5, padx=10)
            elif action is None:
                # Section header
                ttk.Label(sidebar, text=label, 
                          font=("Segoe UI", 8, "bold"),
                          foreground="#666", background="#1a1a2e").pack(anchor="w", padx=15, pady=5)
            else:
                # Clickable item
                btn = ttk.Button(sidebar, text=label, style="Nav.TButton", command=action)
                btn.pack(fill="x", padx=10, pady=2)
        
        return sidebar
    
    def create_topbar(self, parent):
        """Create the top bar with breadcrumbs and actions"""
        topbar = ttk.Frame(parent, style="Topbar.TFrame")
        
        # Breadcrumbs
        self.breadcrumb = ttk.Label(topbar, text="Home", 
                                     font=("Segoe UI", 11),
                                     background="#f8f9fa")
        self.breadcrumb.pack(side="left", padx=20, pady=10)
        
        # Quick actions
        actions_frame = ttk.Frame(topbar, style="Topbar.TFrame")
        actions_frame.pack(side="right", padx=20)
        
        # Quick create dropdown
        quick_create_btn = ttk.Menubutton(actions_frame, text="+ Quick Create")
        quick_menu = tk.Menu(quick_create_btn, tearoff=0)
        quick_menu.add_command(label="Sales Order", command=lambda: self.open_form("Sales Order"))
        quick_menu.add_command(label="Customer", command=lambda: self.open_form("Customer"))
        quick_menu.add_command(label="Item", command=lambda: self.open_form("Item"))
        quick_menu.add_command(label="Supplier", command=lambda: self.open_form("Supplier"))
        quick_create_btn["menu"] = quick_menu
        quick_create_btn.pack(side="left", padx=5)
        
        return topbar
    
    def clear_viewport(self):
        """Clear the main viewport"""
        for widget in self.viewport.winfo_children():
            widget.destroy()
    
    def set_breadcrumb(self, text):
        """Update breadcrumb"""
        self.breadcrumb.config(text=text)
    
    def show_home(self):
        """Show home dashboard"""
        self.clear_viewport()
        self.set_breadcrumb("Home")
        
        # Dashboard
        dashboard = ttk.Frame(self.viewport, style="Content.TFrame")
        dashboard.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Welcome
        ttk.Label(dashboard, text="Welcome to Mini ERPNext", 
                  font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=10)
        ttk.Label(dashboard, text="Your complete sales management system", 
                  font=("Segoe UI", 12)).pack(anchor="w")
        
        # Quick stats
        stats_frame = ttk.Frame(dashboard, style="Content.TFrame")
        stats_frame.pack(fill="x", pady=30)
        
        self.create_stat_card(stats_frame, "Customers", "Customer", 0)
        self.create_stat_card(stats_frame, "Items", "Item", 1)
        self.create_stat_card(stats_frame, "Sales Orders", "Sales Order", 2)
        self.create_stat_card(stats_frame, "Suppliers", "Supplier", 3)
        
        # Quick actions
        ttk.Label(dashboard, text="Quick Actions", 
                  font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=20)
        
        actions_frame = ttk.Frame(dashboard, style="Content.TFrame")
        actions_frame.pack(fill="x")
        
        self.create_action_card(actions_frame, "New Sales Order", "Sales Order", 0)
        self.create_action_card(actions_frame, "New Customer", "Customer", 1)
        self.create_action_card(actions_frame, "New Item", "Item", 2)
    
    def create_stat_card(self, parent, title, doctype, col):
        """Create a statistics card"""
        from core.database import db, get_table_name
        
        card = ttk.Frame(parent, style="Card.TFrame", padding=20)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        
        # Get count
        try:
            table = get_table_name(doctype)
            result = db.sql(f"SELECT COUNT(*) as count FROM {table}", as_dict=True)
            count = result[0]['count'] if result else 0
        except:
            count = 0
        
        ttk.Label(card, text=str(count), font=("Segoe UI", 28, "bold")).pack()
        ttk.Label(card, text=title, font=("Segoe UI", 11)).pack()
        
        # Click to open list
        card.bind("<Button-1>", lambda e: self.open_list(doctype))
        for child in card.winfo_children():
            child.bind("<Button-1>", lambda e, dt=doctype: self.open_list(dt))
    
    def create_action_card(self, parent, title, doctype, col):
        """Create a quick action card"""
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)
        
        ttk.Button(card, text=title, style="Primary.TButton",
                   command=lambda: self.open_form(doctype)).pack(expand=True)
    
    def show_module(self, module_name):
        """Show module workspace"""
        self.clear_viewport()
        self.set_breadcrumb(f"Home > {module_name}")
        
        workspace = ttk.Frame(self.viewport, style="Content.TFrame")
        workspace.pack(fill="both", expand=True, padx=30, pady=20)
        
        ttk.Label(workspace, text=f"{module_name} Module", 
                  font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=10)
        
        # Module-specific shortcuts
        shortcuts = {
            "Selling": [
                ("Sales Orders", "Sales Order"),
                ("Customers", "Customer"),
                ("Quotations", "Quotation"),
            ],
            "Buying": [
                ("Purchase Orders", "Purchase Order"),
                ("Suppliers", "Supplier"),
            ],
            "Stock": [
                ("Items", "Item"),
                ("Warehouses", "Warehouse"),
                ("Stock Entries", "Stock Entry"),
                ("Bins", "Bin"),
            ],
            "Accounts": [
                ("Accounts", "Account"),
                ("GL Entries", "GL Entry"),
            ],
        }
        
        cards_frame = ttk.Frame(workspace, style="Content.TFrame")
        cards_frame.pack(fill="x", pady=20)
        
        for i, (label, doctype) in enumerate(shortcuts.get(module_name, [])):
            card = ttk.Frame(cards_frame, style="Card.TFrame", padding=20)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            cards_frame.columnconfigure(i % 3, weight=1)
            
            ttk.Label(card, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            
            btn_frame = ttk.Frame(card, style="Card.TFrame")
            btn_frame.pack(fill="x", pady=10)
            
            ttk.Button(btn_frame, text="View List", 
                       command=lambda dt=doctype: self.open_list(dt)).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="+ New", style="Primary.TButton",
                       command=lambda dt=doctype: self.open_form(dt)).pack(side="left")
    
    def open_list(self, doctype):
        """Open list view for a doctype"""
        self.clear_viewport()
        self.set_breadcrumb(f"Home > {doctype}")
        
        list_view = ListView(
            self.viewport, 
            doctype,
            on_edit=self.open_form,
            on_create=lambda dt: self.open_form(dt),
            on_back=self.show_home
        )
        list_view.pack(fill="both", expand=True)
    
    def open_form(self, doctype, name=None):
        """Open form view for a doctype"""
        self.clear_viewport()
        title = f"{doctype}: {name}" if name else f"New {doctype}"
        self.set_breadcrumb(f"Home > {doctype} > {title}")
        
        form_view = FormView(
            self.viewport,
            doctype,
            name=name,
            on_back=lambda: self.open_list(doctype)
        )
        form_view.pack(fill="both", expand=True)


def main():
    """Run the Desk application"""
    # Initialize database tables
    import subprocess
    import sys
    
    print("Initializing database...")
    subprocess.run([sys.executable, "-m", "core.schema"], 
                   cwd="d:\\sales_systems", capture_output=True)
    
    app = Desk()
    app.mainloop()


if __name__ == "__main__":
    main()
