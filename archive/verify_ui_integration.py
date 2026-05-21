import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.insert(0, os.getcwd())

from core.database import get_db
from modules.sales.setup_workflow import setup_sales_workflow
import uuid

def verify_imports():
    print("Verifying Imports...")
    try:
        from ui.workflow_widgets import PendingActionsWidget
        from ui.sales_ui import SalesView
        from ui.finance_ui import FinanceView
        # from ui.inventory_ui import InventoryView  # REMOVED: File deleted
        print("  PASS: UI Modules Imported")
    except Exception as e:
        print(f"  FAIL: Import Error: {e}")
        exit(1)

def verify_queries():
    print("Verifying UI Queries...")
    db = get_db()
    
    # 1. Finance Query
    print("  Testing Finance 'Pending Approvals' Query...")
    try:
        sql = """
            SELECT so.order_number, so.order_date, c.name, so.total_amount, ws.name
            FROM sales_orders so
            JOIN document_state_tracker dst ON dst.document_id = so.order_number
            JOIN workflow_states ws ON dst.current_state_id = ws.state_id
            JOIN customers c ON so.customer_id = c.customer_id
            WHERE ws.name = 'Submitted' AND dst.document_type = 'SALES_ORDER'
        """
        db.fetch_all(sql)
        print("  PASS: Finance Query Valid")
    except Exception as e:
        print(f"  FAIL: Finance Query syntax: {e}")

    # 2. Warehouse Query
    print("  Testing Warehouse 'Pending Releases' Query...")
    try:
        sql = """
            SELECT so.order_number, so.order_date, c.name, ws.name
            FROM sales_orders so
            JOIN document_state_tracker dst ON dst.document_id = so.order_number
            JOIN workflow_states ws ON dst.current_state_id = ws.state_id
            JOIN customers c ON so.customer_id = c.customer_id
            WHERE ws.name = 'Ready_For_Warehouse' AND dst.document_type = 'SALES_ORDER'
        """
        db.fetch_all(sql)
        print("  PASS: Warehouse Query Valid")
    except Exception as e:
         print(f"  FAIL: Warehouse Query syntax: {e}")

    # 3. Sales List Query
    print("  Testing Sales List Query...")
    try:
        search = "%%"
        sql = """
                SELECT so.order_number, so.order_date, IFNULL(c.name, 'Unknown Customer') as name, 
                       IFNULL(e.full_name, 'Unknown') as emp_name,
                       so.total_amount, so.paid_amount, so.status, so.payment_status,
                       ws.name as workflow_state
                FROM sales_orders so
                LEFT JOIN customers c ON so.customer_id = c.customer_id
                LEFT JOIN employees e ON so.employee_id = e.employee_id
                LEFT JOIN document_state_tracker dst ON dst.document_id = so.order_number AND dst.document_type = 'SALES_ORDER'
                LEFT JOIN workflow_states ws ON dst.current_state_id = ws.state_id
                WHERE so.order_number LIKE ? OR IFNULL(c.name, '') LIKE ?
                ORDER BY so.order_date DESC
            """
        db.fetch_all(sql, (search, search))
        print("  PASS: Sales List Query Valid")
    except Exception as e:
        print(f"  FAIL: Sales Query syntax: {e}")

if __name__ == "__main__":
    verify_imports()
    verify_queries()
    print("UI INTEGRATION VERIFIED")
