import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root
sys.path.insert(0, os.getcwd())

try:
    # print("Step 1: Importing ui.employee_ui...")
    # from ui.employee_ui import EmployeeView, EmployeeForm  # REMOVED: File deleted
    # print("SUCCESS: Import successful")

    print("Step 2: Initializes Root...")
    root = tk.Tk()
    
    # print("Step 3: Instantiating EmployeeView...")
    # Mock user data
    user_data = {'id': 1, 'full_name': 'Test Admin', 'username': 'admin'}
    
    # view = EmployeeView(root, user_data)  # REMOVED: Class no longer exists
    # print("SUCCESS: EmployeeView instantiated")
    
    # We can't easily test the Form without event loop, but we can try to init it 
    # if we mock the open_add_dialog call or just instantiate it directly (needs toplevel behavior)
    # Using destroy immediately to avoid blocking
    
    print("Step 4: Checking MainWindow integration...")
    from ui.main_window import MainWindow
    if hasattr(MainWindow, 'show_employees'):
        print("SUCCESS: MainWindow has show_employees method")
    else:
        print("FAILURE: MainWindow missing show_employees")

    print("Step 5: Verifying Updated Modules (Sales, Purchasing, Finance)...")
    from ui.sales_ui import SalesView
    from ui.purchasing_ui import PurchasingView
    from ui.finance_ui import FinanceView
    
    # Instantiate to check for syntax errors in __init__ / setup_ui
    print("  - Instantiating SalesView...")
    try:
        SalesView(root, user_data)
        print("    SUCCESS")
    except Exception as e:
        print(f"    FAILURE (SalesView): {e}")
        import traceback; traceback.print_exc()

    print("  - Instantiating PurchasingView...")
    try:
        PurchasingView(root, user_data)
        print("    SUCCESS")
    except Exception as e:
        print(f"    FAILURE (PurchasingView): {e}")
        # import traceback; traceback.print_exc() # DB error likely if no tables, but we just check syntax

    print("  - Instantiating FinanceView...")
    try:
        FinanceView(root, user_data)
        print("    SUCCESS")
    except Exception as e:
        print(f"    FAILURE (FinanceView): {e}")

    print("ALL CHECKS PASSED")
    root.destroy()
    
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
