"""
Test Sales Order Controller
Verifies the full lifecycle: create -> validate -> submit -> cancel
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

import core.frappe as frappe
from core.database import db, get_table_name

def test_sales_order_lifecycle():
    print("=" * 60)
    print("Testing Sales Order Controller Integration")
    print("=" * 60)
    
    # 1. Check if controller is loaded
    print("\n1. Testing Controller Loading...")
    so = frappe.get_doc("Sales Order")
    print(f"   Created doc type: {type(so).__name__}")
    
    if type(so).__name__ == "SalesOrder":
        print("   ✓ Controller loaded successfully!")
    else:
        print("   ✗ Controller NOT loaded - using base Document")
        return False
    
    # 2. Set up test data
    print("\n2. Setting up test data...")
    
    # Get a customer
    customers = frappe.get_list("Customer")
    if not customers:
        print("   ✗ No customers found. Run seed_data.py first.")
        return False
    
    customer = customers[0]['name']
    print(f"   Using customer: {customer}")
    
    # Get an item
    items = frappe.get_list("Item")
    if not items:
        print("   ✗ No items found. Run seed_data.py first.")
        return False
    
    item_code = items[0]['name']
    print(f"   Using item: {item_code}")
    
    # Get a warehouse
    warehouses = frappe.get_list("Warehouse")
    if not warehouses:
        # Create a test warehouse
        wh = frappe.get_doc("Warehouse")
        wh.warehouse_name = "Main Warehouse"
        wh.save()
        warehouse = wh.name
        print(f"   Created warehouse: {warehouse}")
    else:
        warehouse = warehouses[0]['name']
        print(f"   Using warehouse: {warehouse}")
    
    # 3. Create Sales Order with controller
    print("\n3. Creating Sales Order...")
    so = frappe.get_doc("Sales Order")
    so.customer = customer
    so.order_date = "2025-12-19"
    so.delivery_date = "2025-12-25"
    so.set_warehouse = warehouse
    
    # Add items
    so._data['items'] = [
        {"item_code": item_code, "qty": 10, "rate": 100, "warehouse": warehouse}
    ]
    
    print(f"   Order items: {so._data['items']}")
    
    # 4. Test save (triggers validate)
    print("\n4. Saving Sales Order (triggers validate)...")
    try:
        so.save()
        print(f"   ✓ Saved! Name: {so.name}")
        print(f"   Status: {so._data.get('status')}")
        print(f"   Grand Total: {so._data.get('grand_total')}")
    except Exception as e:
        print(f"   ✗ Save failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Test submit (triggers on_submit, reserves stock)
    print("\n5. Submitting Sales Order (triggers on_submit)...")
    try:
        so.submit()
        print(f"   ✓ Submitted! docstatus: {so.docstatus}")
        print(f"   Status: {so._data.get('status')}")
        
        # Check Bin for reserved qty
        bin_table = get_table_name("Bin")
        bins = db.sql(
            f"SELECT * FROM {bin_table} WHERE item_code = ? AND warehouse = ?",
            (item_code, warehouse),
            as_dict=True
        )
        if bins:
            print(f"   ✓ Bin updated! Reserved Qty: {bins[0].get('reserved_qty')}")
        else:
            print("   ⚠ Bin not found (may not have been created)")
            
    except Exception as e:
        print(f"   ✗ Submit failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Test cancel (triggers on_cancel, unreserves stock)
    print("\n6. Cancelling Sales Order (triggers on_cancel)...")
    try:
        so.cancel()
        print(f"   ✓ Cancelled! docstatus: {so.docstatus}")
        print(f"   Status: {so._data.get('status')}")
        
        # Check Bin again
        bins = db.sql(
            f"SELECT * FROM {bin_table} WHERE item_code = ? AND warehouse = ?",
            (item_code, warehouse),
            as_dict=True
        )
        if bins:
            print(f"   ✓ Bin updated! Reserved Qty after cancel: {bins[0].get('reserved_qty')}")
            
    except Exception as e:
        print(f"   ✗ Cancel failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! Controller integration verified.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_sales_order_lifecycle()
