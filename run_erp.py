"""
Run ERP System
New entry point for the Mini-ERP System.
"""
import tkinter as tk
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
import sys
import os

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    root = tk.Tk()
    
    # Simple navigation controller
    def on_login_success(user_data):
        # Destroy login window (which uses root)
        # Actually in Tkinter, root is unique. LoginWindow populates root.
        # We need to clear root and switch to MainWindow
        for widget in root.winfo_children():
            widget.destroy()
            
        # Initialize Main Window
        MainWindow(root, user_data)

    # Start with Login
    LoginWindow(root, on_login_success)
    
    root.mainloop()

if __name__ == "__main__":
    main()
