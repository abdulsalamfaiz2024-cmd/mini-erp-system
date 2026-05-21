
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import core.frappe as frappe

def test_flow():
    print("Testing Core Framework...")
    
    # 1. Create New
    print("Creating new Customer...")
    doc = frappe.get_doc("Customer")
    doc.customer_name = "Test Enterprise"
    doc.customer_type = "Company"
    doc.save()
    print(f"Created Customer: {doc.name}")
    
    name = doc.name
    
    # 2. Load
    print("Loading Customer...")
    doc2 = frappe.get_doc("Customer", name)
    assert doc2.customer_name == "Test Enterprise"
    print("Load Verified.")
    
    # 3. Update
    print("Updating Customer...")
    doc2.customer_name = "Test Enterprise Updated"
    doc2.save()
    
    doc3 = frappe.get_doc("Customer", name)
    assert doc3.customer_name == "Test Enterprise Updated"
    print("Update Verified.")
    
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_flow()
