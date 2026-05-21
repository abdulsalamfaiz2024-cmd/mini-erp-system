"""
Migrate Legacy Data to ERPNext Tables
Transfers data from legacy tables (customers, products) to ERPNext tables (tabcustomer, tabitem).
"""
import sqlite3
from datetime import datetime

DB_PATH = "perfect_sales_system.db"

def migrate_to_erpnext_tables():
    """Migrate from legacy tables to ERPNext-style tables"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("MIGRATING TO ERPNEXT TABLES")
    print("=" * 60)
    
    now = datetime.now().isoformat()
    
    # 1. Migrate Customers -> tabcustomer
    print("\n1. Migrating customers -> tabcustomer")
    cursor.execute("SELECT customer_id, name, business_name, customer_type, phone, email FROM customers")
    customers = cursor.fetchall()
    
    for cust in customers:
        customer_id, name, business_name, customer_type, phone, email = cust
        doc_name = f"CUST-{customer_id}" if customer_id else name.replace(" ", "-").upper()[:20]
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tabcustomer 
                (name, creation, modified, owner, docstatus, customer_name, customer_type, email_id, mobile_no)
                VALUES (?, ?, ?, 'Administrator', 0, ?, ?, ?, ?)
            """, (doc_name, now, now, name or business_name, customer_type or 'Company', email, phone))
            print(f"  Added: {doc_name} ({name})")
        except Exception as e:
            print(f"  Error: {e}")
    
    # 2. Migrate Products -> tabitem
    print("\n2. Migrating products -> tabitem")
    cursor.execute("SELECT product_id, name, category, selling_price, cost_price, unit FROM products")
    products = cursor.fetchall()
    
    for prod in products:
        product_id, name, category, selling_price, cost_price, unit = prod
        doc_name = f"ITEM-{product_id}" if product_id else name.replace(" ", "-").upper()[:20]
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tabitem
                (name, creation, modified, owner, docstatus, item_name, item_group, standard_rate, stock_uom)
                VALUES (?, ?, ?, 'Administrator', 0, ?, ?, ?, ?)
            """, (doc_name, now, now, name, category or 'Products', selling_price or 0, unit or 'Unit'))
            print(f"  Added: {doc_name} ({name})")
        except Exception as e:
            print(f"  Error: {e}")
    
    # 3. Migrate Suppliers -> tabsupplier
    print("\n3. Migrating suppliers -> tabsupplier")
    cursor.execute("SELECT supplier_id, name, contact_person, phone, email FROM suppliers")
    suppliers = cursor.fetchall()
    
    for sup in suppliers:
        supplier_id, name, contact_person, phone, email = sup
        doc_name = f"SUP-{supplier_id}" if supplier_id else name.replace(" ", "-").upper()[:20]
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO tabsupplier
                (name, creation, modified, owner, docstatus, supplier_name, mobile_no)
                VALUES (?, ?, ?, 'Administrator', 0, ?, ?)
            """, (doc_name, now, now, name, phone))
            print(f"  Added: {doc_name} ({name})")
        except Exception as e:
            print(f"  Error: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    migrate_to_erpnext_tables()
