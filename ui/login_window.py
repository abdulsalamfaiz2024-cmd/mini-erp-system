"""
Login Window
Handles user authentication.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import Theme
from modules.security.auth import AuthManager

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Mini-ERP System - Login")
        self.root.geometry("400x500")
        self.root.configure(bg=Theme.BG_MAIN)
        self.on_login_success = on_login_success
        
        Theme.apply_styles(self.root)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure Frame
        self.root.configure(bg=Theme.BG_MAIN)
        
        # Center Frame (Card)
        main_frame = ttk.Frame(self.root, style='Card.TFrame', padding=40)
        main_frame.place(relx=0.5, rely=0.5, anchor='center', width=400)
        
        # Logo/Title
        ttk.Label(main_frame, text="NEXUS ERP", font=("Segoe UI", 24, "bold"), foreground=Theme.PRIMARY, background=Theme.BG_WHITE).pack(pady=(0, 5))
        ttk.Label(main_frame, text="Enterprise Management System", font=("Segoe UI", 10), foreground=Theme.SECONDARY, background=Theme.BG_WHITE).pack(pady=(0, 30))
        
        # Username
        ttk.Label(main_frame, text="Username", font=("Segoe UI", 10, "bold"), background=Theme.BG_WHITE).pack(anchor='w', pady=(0, 5))
        self.user_entry = ttk.Entry(main_frame, font=("Segoe UI", 11))
        self.user_entry.pack(fill='x', pady=(0, 15))
        
        # Password
        ttk.Label(main_frame, text="Password", font=("Segoe UI", 10, "bold"), background=Theme.BG_WHITE).pack(anchor='w', pady=(0, 5))
        self.pass_entry = ttk.Entry(main_frame, show="*", font=("Segoe UI", 11))
        self.pass_entry.pack(fill='x', pady=(0, 25))
        
        # Login Button
        login_btn = ttk.Button(main_frame, text="SECURE LOGIN", command=self.login, style='Primary.TButton', cursor="hand2")
        login_btn.pack(fill='x', ipady=5)
        
        # Default focus
        self.user_entry.focus()
        self.root.bind('<Return>', lambda e: self.login())
        
        # Default Admin Hint
        self.user_entry.insert(0, "admin")
        self.pass_entry.insert(0, "admin123")

    def login(self):
        """
        TEMPORARY BYPASS: Automatically log in as admin.
        User requested to remove authentication temporarily due to login issues.
        """
        # Default Admin User Data
        user_data = {
            'id': 1,
            'username': 'admin',
            'full_name': 'System Administrator',
            'role_id': 1
        }
        
        print("DEBUG: Bypassing Login Check -> Logging in as Admin")
        self.on_login_success(user_data)
