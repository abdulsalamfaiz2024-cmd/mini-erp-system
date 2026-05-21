
import os
from modules.reporting.invoice_generator import InvoiceGenerator
from datetime import datetime

def test_gen():
    order = {
        'order_number': 'INV-2025-001',
        'order_date': '2025-12-15',
        'status': 'paid',
        'subtotal': 100.0,
        'total_tax': 10.0,
        'total_discount': 5.0,
        'total_amount': 105.0
    }
    
    customer = {
        'name': 'Acme Corp',
        'customer_id': 123
    }
    
    items = [
        {
            'name': 'Widget A',
            'quantity': 2,
            'unit_price': 50.0,
            'tax_amount': 5.0,
            'discount_amount': 0.0,
            'total_price': 105.0 # (50*2 + 5 tax)
        },
         {
            'name': 'Widget B',
            'quantity': 1,
            'unit_price': 0.0, # Free sample
            'tax_amount': 0.0,
            'discount_amount': 0.0,
            'total_price': 0.0
        }
    ]
    
    user = {'full_name': 'Test User'}
    
    fn = "test_invoice.pdf"
    if os.path.exists(fn): os.remove(fn)
    
    print("Generating...")
    InvoiceGenerator.generate(fn, order, customer, items, user)
    
    if os.path.exists(fn):
        sz = os.path.getsize(fn)
        print(f"Success. File created. Size: {sz} bytes")
    else:
        print("Failed. File not found.")

if __name__ == "__main__":
    test_gen()
