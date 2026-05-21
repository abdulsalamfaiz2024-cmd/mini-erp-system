"""
UI Styles and Assets
Defines the visual theme for the ERP system (Modern Enterprise).
"""

from tkinter import ttk
import tkinter.font as tkfont

class Theme:
    # --- Color Palette (Modern Slate & Corporate Blue) ---
    PRIMARY         = "#2C3E50"  # Deep Slate (Sidebar/Headers)
    PRIMARY_DARK    = "#1A252F"  # Darker Slate (Active State)
    ACCENT          = "#3498DB"  # Bright Blue (Primary Actions)
    ACCENT_HOVER    = "#2980B9"  # Darker Blue
    
    SECONDARY       = "#95A5A6"  # Gray (Inactive/Secondary)
    
    SUCCESS         = "#27AE60"  # Emerald Green
    WARNING         = "#F39C12"  # Amber
    DANGER          = "#C0392B"  # Pomegranate Red
    INFO            = "#16A085"  # Teal
    
    BG_MAIN         = "#ECF0F1"  # Very Light Gray (App Background)
    BG_WHITE        = "#FFFFFF"  # Cards/Content
    
    TEXT_MAIN       = "#2C3E50"  # Dark for readability
    TEXT_PRIMARY    = "#2C3E50"  # Same as TEXT_MAIN
    TEXT_MUTED      = "#7F8C8D"  # Gray for labels
    TEXT_WHITE      = "#FFFFFF"
    
    PRIMARY_LIGHT   = "#3E5266"  # Lighter slate for hover
    BORDER_LIGHT    = "#BDC3C7"  # Subtle borders

    # --- Typography ---
    FONT_FAMILY     = "Segoe UI"
    
    @staticmethod
    def fonts():
        return {
            "h1": (Theme.FONT_FAMILY, 24, "bold"),
            "h2": (Theme.FONT_FAMILY, 18, "bold"),
            "h3": (Theme.FONT_FAMILY, 14, "bold"),
            "body": (Theme.FONT_FAMILY, 10),
            "body_b": (Theme.FONT_FAMILY, 10, "bold"),
            "small": (Theme.FONT_FAMILY, 9),
        }

    # --- Charting Colors ---
    CHART_BARS      = ["#3498DB", "#2ECC71", "#9B59B6", "#F1C40F", "#E74C3C"]
    
    @staticmethod
    def apply_styles(root):
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- General Reset ---
        style.configure(".", background=Theme.BG_MAIN, foreground=Theme.TEXT_MAIN, font=("Segoe UI", 10))
        
        # --- Layouts ---
        style.configure('Main.TFrame', background=Theme.BG_MAIN)
        style.configure('Sidebar.TFrame', background=Theme.PRIMARY)
        style.configure('Card.TFrame', background=Theme.BG_WHITE, relief="flat", borderwidth=0)
        style.configure('White.TFrame', background=Theme.BG_WHITE)

        # --- Typography ---
        style.configure('H1.TLabel', font=("Segoe UI", 26, "bold"), background=Theme.BG_MAIN, foreground=Theme.PRIMARY)
        style.configure('H2.TLabel', font=("Segoe UI", 16, "bold"), background=Theme.BG_MAIN, foreground=Theme.PRIMARY)
        style.configure('CardTitle.TLabel', font=("Segoe UI", 14, "bold"), background=Theme.BG_WHITE, foreground=Theme.PRIMARY)
        style.configure('CardMetric.TLabel', font=("Segoe UI", 28, "bold"), background=Theme.BG_WHITE, foreground=Theme.PRIMARY)
        style.configure('CardSub.TLabel', font=("Segoe UI", 10), background=Theme.BG_WHITE, foreground=Theme.TEXT_MUTED)
        
        style.configure('Sidebar.TLabel', background=Theme.PRIMARY, foreground=Theme.TEXT_WHITE, font=("Segoe UI", 10, "bold"))
        style.configure('SidebarHeader.TLabel', background=Theme.PRIMARY, foreground=Theme.SECONDARY, font=("Segoe UI", 9, "bold"))
        
        # Compatibility
        style.configure('Title.TLabel', font=("Segoe UI", 22, "bold"), background=Theme.BG_MAIN, foreground=Theme.PRIMARY)
        style.configure('Header.TLabel', font=("Segoe UI", 14, "bold"), background=Theme.BG_MAIN, foreground=Theme.PRIMARY)
        style.configure('Label', background=Theme.BG_WHITE, foreground=Theme.TEXT_MAIN)

        # --- Interactive Elements ---
        # Primary Button (Flat, clean)
        style.configure('Primary.TButton', 
            font=("Segoe UI", 10, "bold"), 
            background=Theme.ACCENT, 
            foreground=Theme.TEXT_WHITE, 
            borderwidth=0, 
            focusthickness=0,
            padding=10
        )
        style.map('Primary.TButton', 
            background=[('active', Theme.ACCENT_HOVER), ('pressed', Theme.PRIMARY_DARK)]
        )
        
        # Danger Button
        style.configure('Danger.TButton', background=Theme.DANGER, foreground=Theme.TEXT_WHITE, borderwidth=0, padding=10)
        style.map('Danger.TButton', background=[('active', '#C0392B')])

        # --- Data Displays (Tables) ---
        style.configure("Treeview", 
            background=Theme.BG_WHITE,
            foreground=Theme.TEXT_MAIN,
            rowheight=40, # Executive spacing
            fieldbackground=Theme.BG_WHITE,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure("Treeview.Heading", 
            font=("Segoe UI", 10, "bold"), 
            background=Theme.BG_MAIN, 
            foreground=Theme.TEXT_MUTED,
            relief="flat"
        )
        style.map("Treeview", 
            background=[('selected', Theme.ACCENT)], 
            foreground=[('selected', Theme.TEXT_WHITE)]
        )
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        # --- TAG STYLES (For Row coloring) ---
        # We can't style specific cells easily in Tkinter, but we can style rows via tags.
        # We will use tags for Statuses.
        style.configure("Paid.Treeview", foreground=Theme.SUCCESS)
        style.configure("Pending.Treeview", foreground=Theme.WARNING)
        style.configure("Overdue.Treeview", foreground=Theme.DANGER)
        style.configure("Invoiced.Treeview", foreground=Theme.INFO)
        style.configure("Completed.Treeview", foreground=Theme.PRIMARY)

        # --- Modern Forms ---
        # Entry
        style.configure('Modern.TEntry', 
            fieldbackground=Theme.BG_WHITE, 
            borderwidth=0, 
            relief='flat', 
            padding=10
        )
        # Combobox
        style.configure('Modern.TCombobox', 
            fieldbackground=Theme.BG_WHITE, 
            background=Theme.BG_WHITE,
            arrowcolor=Theme.PRIMARY,
            borderwidth=0,
            relief='flat',
            padding=10
        )
        
        # Overlay / Modal Background
        style.configure('Overlay.TFrame', background="#000000") # Will use alpha via canvas usually, or simple frame

