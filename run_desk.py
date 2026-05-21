"""
Mini ERPNext - Main Entry Point
Launch the professional ERPNext-style Desk interface.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database
print("Initializing database schema...")
from core.schema import sync_all_doctypes
sync_all_doctypes()

# Launch Desk
print("Starting Mini ERPNext Desk...")
from ui.framework.desk import Desk

if __name__ == "__main__":
    app = Desk()
    app.mainloop()
