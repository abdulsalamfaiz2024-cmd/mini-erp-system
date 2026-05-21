"""
Runtime UI Verification Script
Tests each page's data loading capability and logs actual runtime status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import get_db
import traceback

def verify_database_contents():
    """Check if database has actual data"""
    db = get_db()
    
    tables_to_check = {
        'sales_orders': 'SELECT COUNT(*) as cnt FROM sales_orders',
        'customers': 'SELECT COUNT(*) as cnt FROM customers',
        'expenses': 'SELECT COUNT(*) as cnt FROM expenses',
        'inventory': 'SELECT COUNT(*) as cnt FROM inventory',
        'employees': 'SELECT COUNT(*) as cnt FROM employees',
        'purchase_orders': 'SELECT name FROM sqlite_master WHERE type="table" AND name="purchase_orders"',
        'journal_entries': 'SELECT name FROM sqlite_master WHERE type="table" AND name="journal_entries"',
        'assets': 'SELECT name FROM sqlite_master WHERE type="table" AND name="assets"',        'suppliers': 'SELECT name FROM sqlite_master WHERE type="table" AND name="suppliers"',
    }
    
    print("=" * 70)
    print("DATABASE CONTENT VERIFICATION")
    print("=" * 70)
    
    results = {}
    for table, query in tables_to_check.items():
        try:
            rows = db.fetch_all(query)
            if 'cnt' in rows[0].keys():
                count = rows[0]['cnt']
                results[table] = {'exists': True, 'count': count}
                print(f"{table:25} EXISTS  | Rows: {count}")
            else:
                exists = len(rows) > 0
                results[table] = {'exists': exists, 'count': 'N/A'}
                print(f"{table:25} {'EXISTS' if exists else 'MISSING'}")
        except Exception as e:
            results[table] = {'exists': False, 'error': str(e)}
            print(f"{table:25} ERROR   | {str(e)[:40]}")
    
    return results

def test_page_sql_queries():
    """Test actual SQL queries from each page"""
    db = get_db()
    
    page_queries = {
        'CustomersPage': """
            SELECT customer_id, name, email, phone, balance
            FROM customers
            ORDER BY name
            LIMIT 100
        """,
        'ExpensesPage': """
            SELECT expense_id, expense_date, amount, category, status,description
            FROM expenses
            ORDER BY expense_date DESC
            LIMIT 100
        """,
        'InventoryStockPage': """
            SELECT 
                i.product_id,
                p.name as product_name,
                SUM(i.quantity) as total_qty,
                i.warehouse_id,
                i.cost_price
            FROM inventory i
            LEFT JOIN products p ON i.product_id = p.product_id
            GROUP BY i.product_id, i.warehouse_id
            ORDER BY p.name
        """,
        'PurchasingPage': """
            SELECT po_number, po_date, 'Supplier' as supplier, 
                   total_amount, status
            FROM purchase_orders
            ORDER BY po_date DESC
            LIMIT 50
        """,
        'JournalEntriesPage': """
            SELECT entry_id, entry_date, description, is_posted
            FROM journal_entries
            ORDER BY entry_date DESC
            LIMIT 100
        """,
        'EmployeesPage': """
            SELECT employee_id, full_name, department, position, 
                   approval_level, status
            FROM employees
            ORDER BY full_name
            LIMIT 100
        """,
    }
    
    print("\n" + "=" * 70)
    print("PAGE SQL QUERY VERIFICATION")
    print("=" * 70)
    
    results = {}
    for page_name, query in page_queries.items():
        try:
            rows = db.fetch_all(query)
            results[page_name] = {'success': True, 'row_count': len(rows)}
            print(f"{page_name:25} OK      | Loaded {len(rows)} rows")
        except Exception as e:
            results[page_name] = {'success': False, 'error': str(e)}
            print(f"{page_name:25} FAILED  | {str(e)[:40]}")
    
    return results

def verify_page_routing():
    """Check if page router has proper mappings"""
    print("\n" + "=" * 70)
    print("PAGE ROUTING VERIFICATION")
    print("=" * 70)
    
    # Import main window to check routing
    try:
        from ui.main_window import MainWindow
        
        # Check page_map
        routes = {
            'finance': 'show_finance',
            'ledger': 'show_ledger',
            'suppliers': 'show_suppliers',
            'expenses': 'show_expenses',
            'inventory': 'show_inventory',
            'purchasing': 'show_purchasing',
            'accounting': 'show_accounting',
            'employees': 'show_employees',
            'customers': 'show_customers',
            'reports': 'show_reports',
        }
        
        for route, method_name in routes.items():
            has_method = hasattr(MainWindow, method_name)
            print(f"{route:20} -> {method_name:25} {'✅ EXISTS' if has_method else '❌ MISSING'}")
            
    except Exception as e:
        print(f"ERROR loading MainWindow: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("RUNTIME UI VERIFICATION SCRIPT")
    print("Running actual database queries from page implementations\n")
    
    db_results = verify_database_contents()
    sql_results = test_page_sql_queries()
    verify_page_routing()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    # Count failures
    db_failures = sum(1 for r in db_results.values() if not r.get('exists', False))
    sql_failures = sum(1 for r in sql_results.values() if not r.get('success', False))
    
    print(f"Database Tables:   {len(db_results) - db_failures}/{len(db_results)} exist")
    print(f"Page SQL Queries:  {len(sql_results) - sql_failures}/{len(sql_results)} working")
    
    if db_failures > 0 or sql_failures > 0:
        print("\n⚠️  FAILURES DETECTED - Pages may show empty data")
    else:
        print("\n✅ All pages have database backing")
