"""
Desk Theme and Styles
ERPNext v15-inspired design system.
"""
from tkinter import ttk


def apply_desk_theme(root):
    """Apply ERPNext-style theme to application"""
    style = ttk.Style()
    
    # Color palette
    colors = {
        "primary": "#2490ef",
        "primary_dark": "#1a73e8",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "sidebar_bg": "#1a1a2e",
        "sidebar_hover": "#2d2d44",
        "topbar_bg": "#f8f9fa",
        "content_bg": "#ffffff",
        "card_bg": "#ffffff",
        "border": "#e0e0e0",
        "text": "#333333",
        "text_muted": "#666666",
    }
    
    # Configure root
    root.configure(bg=colors["content_bg"])
    
    # ===== Frame Styles =====
    style.configure("Desk.TFrame", background=colors["content_bg"])
    style.configure("Sidebar.TFrame", background=colors["sidebar_bg"])
    style.configure("Topbar.TFrame", background=colors["topbar_bg"])
    style.configure("Content.TFrame", background=colors["content_bg"])
    style.configure("Card.TFrame", background=colors["card_bg"], relief="solid", borderwidth=1)
    
    # ===== Label Styles =====
    style.configure("TLabel", background=colors["content_bg"], foreground=colors["text"])
    style.configure("Sidebar.TLabel", background=colors["sidebar_bg"], foreground="white")
    
    # ===== Button Styles =====
    style.configure("TButton",
                    padding=(15, 8),
                    font=("Segoe UI", 10))
    
    style.configure("Primary.TButton",
                    padding=(15, 8),
                    font=("Segoe UI", 10, "bold"))
    
    style.map("Primary.TButton",
              background=[("active", colors["primary_dark"]), ("!active", colors["primary"])],
              foreground=[("active", "white"), ("!active", "white")])
    
    # Navigation button
    style.configure("Nav.TButton",
                    padding=(10, 8),
                    font=("Segoe UI", 10),
                    anchor="w")
    
    style.map("Nav.TButton",
              background=[("active", colors["sidebar_hover"]), ("!active", colors["sidebar_bg"])],
              foreground=[("active", "white"), ("!active", "#cccccc")])
    
    # ===== Entry Styles =====
    style.configure("TEntry",
                    padding=8,
                    font=("Segoe UI", 10))
    
    # ===== Combobox Styles =====
    style.configure("TCombobox",
                    padding=8,
                    font=("Segoe UI", 10))
    
    # ===== Treeview Styles =====
    style.configure("Treeview",
                    font=("Segoe UI", 10),
                    rowheight=30,
                    background=colors["content_bg"],
                    fieldbackground=colors["content_bg"])
    
    style.configure("Treeview.Heading",
                    font=("Segoe UI", 10, "bold"),
                    padding=8)
    
    style.map("Treeview",
              background=[("selected", colors["primary"])],
              foreground=[("selected", "white")])
    
    # ===== Separator =====
    style.configure("TSeparator", background=colors["border"])
    
    # ===== LabelFrame =====
    style.configure("TLabelframe", background=colors["content_bg"])
    style.configure("TLabelframe.Label", 
                    background=colors["content_bg"],
                    foreground=colors["text"],
                    font=("Segoe UI", 10, "bold"))
    
    # ===== Menubutton =====
    style.configure("TMenubutton",
                    padding=(10, 8),
                    font=("Segoe UI", 10))
    
    return style
