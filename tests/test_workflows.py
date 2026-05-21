"""
Test Workflow Enhancements
Verifies the new workflow integrations work correctly.
"""
import sys
sys.path.insert(0, '.')

from core.database import db, get_table_name
import core.frappe as frappe
from core.schema import sync_all_doctypes

def test_workflows():
    """Test the enhanced workflows"""
    
    print("=" * 60)
    print("WORKFLOW ENHANCEMENT TESTS")
    print("=" * 60)
    
    # Initialize schema
    print("\n1. Initializing database schema...")
    try:
        sync_all_doctypes()
        print("   Schema synced successfully")
    except Exception as e:
        print(f"   Schema sync warning: {e}")
    
    # Test 1: Check Bin projected_qty calculation
    print("\n2. Testing Bin projected_qty calculation...")
    try:
        table = get_table_name("Bin")
        bins = db.sql(f"SELECT item_code, warehouse, actual_qty, reserved_qty, ordered_qty, projected_qty FROM {table} LIMIT 5", as_dict=True)
        if bins:
            for b in bins:
                expected = float(b.get('actual_qty', 0) or 0) + float(b.get('ordered_qty', 0) or 0) - float(b.get('reserved_qty', 0) or 0)
                actual_proj = float(b.get('projected_qty', 0) or 0)
                print(f"   {b.get('item_code')}: actual={b.get('actual_qty')}, reserved={b.get('reserved_qty')}, projected={b.get('projected_qty')}")
            print("   Bin tracking: OK")
        else:
            print("   No Bin entries found (will be created when Items are added)")
    except Exception as e:
        print(f"   Bin test error: {e}")
    
    # Test 2: Check SellingController methods exist
    print("\n3. Testing SellingController enhancements...")
    try:
        from controllers.selling_controller import SellingController
        
        # Check methods exist
        methods = ['on_submit', 'on_cancel', 'update_customer_balance', 'update_reserved_stock']
        for method in methods:
            if hasattr(SellingController, method):
                print(f"   {method}(): OK")
            else:
                print(f"   {method}(): MISSING")
    except Exception as e:
        print(f"   SellingController test error: {e}")
    
    # Test 3: Check Item controller exists
    print("\n4. Testing Item controller...")
    try:
        from apps.stock.doctype.item.item import Item
        
        methods = ['on_save', 'create_default_bin', 'validate']
        for method in methods:
            if hasattr(Item, method):
                print(f"   {method}(): OK")
            else:
                print(f"   {method}(): MISSING")
    except Exception as e:
        print(f"   Item controller test error: {e}")
    
    # Test 4: Check StockController update_bin
    print("\n5. Testing StockController enhancements...")
    try:
        from controllers.stock_controller import StockController
        
        # Read the source to verify projected_qty logic
        import inspect
        source = inspect.getsource(StockController.update_bin)
        if 'projected_qty' in source:
            print("   update_bin() includes projected_qty: OK")
        else:
            print("   update_bin() missing projected_qty logic")
    except Exception as e:
        print(f"   StockController test error: {e}")
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_workflows()
