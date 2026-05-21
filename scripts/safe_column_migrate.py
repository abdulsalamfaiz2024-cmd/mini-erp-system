"""
Safe Column Migration
Transfers data from legacy tables (perfect_sales_system.db) to ERPNext tables (sales_system.db).
Only transfers matching/compatible columns. Does NOT change any paths.
"""
import sqlite3
from datetime import datetime
import uuid

# Source: Your data with Arabic names
SOURCE_DB = "perfect_sales_system.db"

# Target: Where the UI reads from  
TARGET_DB = "sales_system.db"

def generate_name():
    """Generate a unique document name"""
    return str(uuid.uuid4())[:8].upper()

def safe_migrate():
    """Safely migrate data between databases"""
    
    print("=" * 60)
    print("SAFE COLUMN MIGRATION")
    print(f"From: {SOURCE_DB} -> To: {TARGET_DB}")
    print("=" * 60)
    
    # Connect to both databases
    source_conn = sqlite3.connect(SOURCE_DB)
    source_conn.text_factory = str
    source = source_conn.cursor()
    
    target_conn = sqlite3.connect(TARGET_DB)
    target_conn.text_factory = str
    target = target_conn.cursor()
    
    now = datetime.now().isoformat()
    
    # 1. CUSTOMERS: customers -> tabcustomer
    print("\n1. Migrating CUSTOMERS...")
    try:
        source.execute("SELECT customer_id, name, business_name, customer_type, phone, email FROM customers")
        customers = source.fetchall()
        
        migrated = 0
        for cust in customers:
            customer_id, name, business_name, customer_type, phone, email = cust
            doc_name = f"CUST-{customer_id}" if customer_id else generate_name()
            customer_name = name or business_name or "Unknown"
            
            try:
                target.execute("""
                    INSERT OR REPLACE INTO tabcustomer 
                    (name, creation, modified, owner, docstatus, customer_name, customer_type, email_id, mobile_no)
                    VALUES (?, ?, ?, 'Administrator', 0, ?, ?, ?, ?)
                """, (doc_name, now, now, customer_name, customer_type or 'Company', email, phone))
                migrated += 1
            except Exception as e:
                print(f"    Skip customer: {e}")
        
        print(f"    Migrated: {migrated} customers")
    except Exception as e:
        print(f"    Error: {e}")
    
    # 2. PRODUCTS -> tabitem
    print("\n2. Migrating PRODUCTS...")
    try:
        source.execute("SELECT product_id, name, category, selling_price, cost_price, unit FROM products")
        products = source.fetchall()
        
        migrated = 0
        for prod in products:
            product_id, name, category, selling_price, cost_price, unit = prod
            doc_name = f"ITEM-{product_id}" if product_id else generate_name()
            item_name = name or "Unknown Product"
            
            try:
                target.execute("""
                    INSERT OR REPLACE INTO tabitem
                    (name, creation, modified, owner, docstatus, item_name, item_group, standard_rate, stock_uom)
                    VALUES (?, ?, ?, 'Administrator', 0, ?, ?, ?, ?)
                """, (doc_name, now, now, item_name, category or 'Products', selling_price or 0, unit or 'Unit'))
                migrated += 1
            except Exception as e:
                print(f"    Skip product: {e}")
        
        print(f"    Migrated: {migrated} products")
    except Exception as e:
        print(f"    Error: {e}")
    
    # 3. SUPPLIERS -> tabsupplier
    print("\n3. Migrating SUPPLIERS...")
    try:
        source.execute("SELECT supplier_id, name, contact_person, phone, email FROM suppliers")
        suppliers = source.fetchall()
        
        migrated = 0
        for sup in suppliers:
            supplier_id, name, contact_person, phone, email = sup
            doc_name = f"SUP-{supplier_id}" if supplier_id else generate_name()
            supplier_name = name or "Unknown Supplier"
            
            try:
                target.execute("""
                    INSERT OR REPLACE INTO tabsupplier
                    (name, creation, modified, owner, docstatus, supplier_name, mobile_no)
                    VALUES (?, ?, ?, 'Administrator', 0, ?, ?)
                """, (doc_name, now, now, supplier_name, phone))
                migrated += 1
            except Exception as e:
                print(f"    Skip supplier: {e}")
        
        print(f"    Migrated: {migrated} suppliers")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Commit and close
    target_conn.commit()
    source_conn.close()
    target_conn.close()
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE - No paths changed")
    print("=" * 60)

if __name__ == "__main__":
    safe_migrate()
