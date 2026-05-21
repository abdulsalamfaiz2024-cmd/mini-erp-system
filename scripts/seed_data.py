
import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../")

import core.frappe as frappe

def seed():
    print("Seeding Data...")
    
    # 1. Create Items
    items = ["Laptop", "Mouse", "Keyboard", "Monitor", "Printer"]
    for i in items:
        if not frappe.db.exists("Item", i):
            doc = frappe.get_doc("Item")
            doc.item_code = i
            doc.item_name = f"{i} Pro"
            doc.standard_rate = random.randint(50, 2000)
            doc.save()
            print(f"Created Item: {i}")

    # 2. Create Customers
    customers = ["Tech Corp", "Alpha Industries", "Beta Ltd", "Gamma LLC"]
    for c in customers:
        name = c.replace(" ", "")[:10]
        # Check if exists by name not fully right but ok for seed
        # Real system we check ID. 
        # Here we just make new ones blindly for demo volume
        doc = frappe.get_doc("Customer")
        doc.customer_name = c
        doc.customer_type = "Company"
        doc.save()
        print(f"Created Customer: {doc.name}")

    # 3. Create Sales Order with Items
    cust = frappe.get_list("Customer")[0]
    
    so = frappe.get_doc("Sales Order")
    so.customer = cust['name']
    so.order_date = "2025-12-19"
    
    # Add items (Child Table)
    so.items = [
        {"item_code": "Laptop", "qty": 2, "rate": 1500, "amount": 3000},
        {"item_code": "Mouse", "qty": 5, "rate": 20, "amount": 100}
    ]
    
    so.grand_total = 3100
    # print("DEBUG SO DATA:", so.as_dict())
    so.save()
    print(f"Created Sales Order: {so.name} with items.")
    
    # Verify Items Saved
    so_loaded = frappe.get_doc("Sales Order", so.name)
    if not so_loaded.items or len(so_loaded.items) != 2:
        print("ERROR: Items not saved!")
    else:
        print(f"SUCCESS: Sales Order {so.name} has {len(so_loaded.items)} items.")

if __name__ == "__main__":
    seed()
