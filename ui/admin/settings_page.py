"""
Settings Page
System settings interface using BasePage pattern
"""

from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
import tkinter as tk


class SettingsPage(BasePage):
    """Settings page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Settings")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'Save Settings',
                'command': self.save_settings,
                'icon': '💾',
                'style': 'Success.TButton'
            }
        ])
    
    def setup_content(self):
        """Build page content"""
        settings_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=40)
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            settings_frame,
            text="⚙️ System Settings",
            style='CardTitle.TLabel',
            font=('Segoe UI', 18, 'bold')
        ).pack(anchor='w', pady=(0, 30))
        
        # User info section
        user_section = ttk.Frame(settings_frame, style='Card.TFrame')
        user_section.pack(fill='x', pady=(0, 20))
        
        ttk.Label(user_section, text="User Information", font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=( 0, 10))
        
        ttk.Label(user_section, text=f"Username: {self.user_data['username']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(user_section, text=f"Full Name: {self.user_data['full_name']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        ttk.Label(user_section, text=f"User ID: {self.user_data['id']}", font=('Segoe UI', 10)).pack(anchor='w', pady=2)
        
        # Placeholder for future settings
        ttk.Separator(settings_frame, orient='horizontal').pack(fill='x', pady=20)
        
        ttk.Label(
            settings_frame,
            text="Additional settings will be available in future updates.",
            font=('Segoe UI', 10),
            foreground='gray'
        ).pack(anchor='w')
    
    def load_data(self):
        """Load settings"""
        # Nothing to load for now
        pass
    
    def save_settings(self):
        """Save settings"""
        messagebox.showinfo("Settings", "Settings saved successfully")
