"""
Professional Theme - Navy Blue + Orange
All styles for the Mini ERPNext application.
"""
from tkinter import ttk
import tkinter as tk


class Theme:
    """Color palette and style constants"""
    
    # Primary Colors
    PRIMARY = "#1F4E79"
    PRIMARY_DARK = "#153759"
    PRIMARY_LIGHT = "#2A5F8F"
    
    # Accent
    ACCENT = "#F5A623"
    ACCENT_DARK = "#D4901F"
    
    # Status Colors
    SUCCESS = "#28A745"
    SUCCESS_DARK = "#218838"
    DANGER = "#DC3545"
    DANGER_DARK = "#C82333"
    WARNING = "#FFC107"
    INFO = "#17A2B8"
    
    # Backgrounds
    BG_LIGHT = "#F9F9F9"
    BG_WHITE = "#FFFFFF"
    BG_SIDEBAR = "#1F4E79"
    BG_TOPBAR = "#FFFFFF"
    
    # Text
    TEXT_DARK = "#333333"
    TEXT_MUTED = "#6C757D"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_LINK = "#1F4E79"
    
    # Borders
    BORDER = "#DEE2E6"
    BORDER_DARK = "#CED4DA"
    
    # Shadows (for reference)
    SHADOW = "#00000020"
    
    # Font - Use braces for font family with spaces
    FONT_FAMILY = "{Segoe UI}"
    FONT_SIZE_H1 = 24
    FONT_SIZE_H2 = 18
    FONT_SIZE_H3 = 14
    FONT_SIZE_BODY = 11
    FONT_SIZE_SMALL = 9


def apply_desk_theme(root):
    """Apply the professional Navy Blue + Orange theme"""
    style = ttk.Style()
    
    # Configure root window
    root.configure(bg=Theme.BG_LIGHT)
    root.option_add("*Font", f"{Theme.FONT_FAMILY} {Theme.FONT_SIZE_BODY}")
    
    # =====================
    # FRAME STYLES
    # =====================
    style.configure("TFrame", background=Theme.BG_LIGHT)
    style.configure("Desk.TFrame", background=Theme.BG_LIGHT)
    style.configure("Content.TFrame", background=Theme.BG_WHITE)
    style.configure("Sidebar.TFrame", background=Theme.BG_SIDEBAR)
    style.configure("Topbar.TFrame", background=Theme.BG_WHITE)
    
    # Card style
    style.configure("Card.TFrame", 
                    background=Theme.BG_WHITE,
                    relief="flat")
    
    # =====================
    # LABEL STYLES
    # =====================
    style.configure("TLabel",
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY))
    
    style.configure("Sidebar.TLabel",
                    background=Theme.BG_SIDEBAR,
                    foreground=Theme.TEXT_LIGHT,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY))
    
    style.configure("H1.TLabel",
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H1, "bold"))
    
    style.configure("H2.TLabel",
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H2, "bold"))
    
    style.configure("H3.TLabel",
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H3, "bold"))
    
    style.configure("Muted.TLabel",
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_MUTED,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))
    
    style.configure("Status.TLabel",
                    background=Theme.BG_WHITE,
                    foreground=Theme.PRIMARY,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"))
    
    # =====================
    # BUTTON STYLES
    # =====================
    
    # Default button
    style.configure("TButton",
                    padding=(15, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK,
                    borderwidth=1,
                    relief="solid")
    
    style.map("TButton",
              background=[("active", Theme.BG_LIGHT), ("pressed", Theme.BORDER)],
              relief=[("pressed", "sunken")])
    
    # Primary button (Navy Blue)
    style.configure("Primary.TButton",
                    padding=(15, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"),
                    background=Theme.PRIMARY,
                    foreground=Theme.TEXT_LIGHT)
    
    style.map("Primary.TButton",
              background=[("active", Theme.PRIMARY_DARK), ("pressed", Theme.PRIMARY_DARK)],
              foreground=[("active", Theme.TEXT_LIGHT)])
    
    # Success button (Green)
    style.configure("Success.TButton",
                    padding=(15, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"),
                    background=Theme.SUCCESS,
                    foreground=Theme.TEXT_LIGHT)
    
    style.map("Success.TButton",
              background=[("active", Theme.SUCCESS_DARK), ("pressed", Theme.SUCCESS_DARK)])
    
    # Danger button (Red)
    style.configure("Danger.TButton",
                    padding=(15, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"),
                    background=Theme.DANGER,
                    foreground=Theme.TEXT_LIGHT)
    
    style.map("Danger.TButton",
              background=[("active", Theme.DANGER_DARK), ("pressed", Theme.DANGER_DARK)])
    
    # Accent button (Orange)
    style.configure("Accent.TButton",
                    padding=(15, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"),
                    background=Theme.ACCENT,
                    foreground=Theme.TEXT_DARK)
    
    style.map("Accent.TButton",
              background=[("active", Theme.ACCENT_DARK), ("pressed", Theme.ACCENT_DARK)])
    
    # Navigation button (Sidebar)
    style.configure("Nav.TButton",
                    padding=(12, 10),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    background=Theme.BG_SIDEBAR,
                    foreground=Theme.TEXT_LIGHT,
                    anchor="w",
                    borderwidth=0)
    
    style.map("Nav.TButton",
              background=[("active", Theme.PRIMARY_LIGHT), ("pressed", Theme.PRIMARY_LIGHT)],
              foreground=[("active", Theme.TEXT_LIGHT)])
    
    # Link button (text only)
    style.configure("Link.TButton",
                    padding=(5, 3),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_LINK,
                    borderwidth=0)
    
    style.map("Link.TButton",
              foreground=[("active", Theme.PRIMARY_DARK)])
    
    # =====================
    # ENTRY STYLES
    # =====================
    style.configure("TEntry",
                    padding=10,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    fieldbackground=Theme.BG_WHITE,
                    borderwidth=1,
                    relief="solid")
    
    style.map("TEntry",
              fieldbackground=[("focus", Theme.BG_WHITE)],
              bordercolor=[("focus", Theme.PRIMARY)])
    
    # =====================
    # COMBOBOX STYLES
    # =====================
    style.configure("TCombobox",
                    padding=8,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    fieldbackground=Theme.BG_WHITE)
    
    # =====================
    # TREEVIEW STYLES
    # =====================
    style.configure("Treeview",
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    rowheight=35,
                    background=Theme.BG_WHITE,
                    fieldbackground=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK)
    
    style.configure("Treeview.Heading",
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"),
                    padding=10,
                    background=Theme.BG_LIGHT,
                    foreground=Theme.TEXT_DARK)
    
    style.map("Treeview",
              background=[("selected", Theme.PRIMARY)],
              foreground=[("selected", Theme.TEXT_LIGHT)])
    
    # =====================
    # SEPARATOR
    # =====================
    style.configure("TSeparator", background=Theme.BORDER)
    
    # =====================
    # LABELFRAME
    # =====================
    style.configure("TLabelframe",
                    background=Theme.BG_WHITE,
                    borderwidth=1,
                    relief="solid")
    
    style.configure("TLabelframe.Label",
                    background=Theme.BG_WHITE,
                    foreground=Theme.TEXT_DARK,
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_H3, "bold"))
    
    # =====================
    # NOTEBOOK (Tabs)
    # =====================
    style.configure("TNotebook",
                    background=Theme.BG_LIGHT,
                    borderwidth=0)
    
    style.configure("TNotebook.Tab",
                    padding=(15, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    background=Theme.BG_LIGHT,
                    foreground=Theme.TEXT_DARK)
    
    style.map("TNotebook.Tab",
              background=[("selected", Theme.BG_WHITE)],
              foreground=[("selected", Theme.PRIMARY)])
    
    # =====================
    # MENUBUTTON
    # =====================
    style.configure("TMenubutton",
                    padding=(12, 8),
                    font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY),
                    background=Theme.BG_WHITE)
    
    # =====================
    # SCROLLBAR
    # =====================
    style.configure("Vertical.TScrollbar",
                    background=Theme.BG_LIGHT,
                    troughcolor=Theme.BG_WHITE,
                    borderwidth=0,
                    arrowsize=14)
    
    style.configure("Horizontal.TScrollbar",
                    background=Theme.BG_LIGHT,
                    troughcolor=Theme.BG_WHITE,
                    borderwidth=0,
                    arrowsize=14)
    
    # =====================
    # PROGRESSBAR
    # =====================
    style.configure("TProgressbar",
                    background=Theme.PRIMARY,
                    troughcolor=Theme.BG_LIGHT,
                    borderwidth=0)
    
    return style


def create_card(parent, title=None, padding=20):
    """Create a card-style frame with optional title"""
    card = ttk.Frame(parent, style="Card.TFrame", padding=padding)
    
    # Add subtle border effect
    card.configure(borderwidth=1, relief="solid")
    
    if title:
        ttk.Label(card, text=title, style="H3.TLabel").pack(anchor="w", pady=(0, 10))
    
    return card
