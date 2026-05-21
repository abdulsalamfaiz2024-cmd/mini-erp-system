import pandas as pd
import sqlite3
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import Database, get_db
from core.config import DATABASE_CONFIG

EXCEL_FILE = "rale_data.xlsx"
DB_FILE = "perfect_sales_system.db"

def clean_date(date_val):
    """Convert Excel date to ISO format YYYY-MM-DD"""
    if pd.isna(date_val):
        return None
    try:
        return pd.to_datetime(date_val).date().isoformat()
    except:
        return None

def clean_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def clean_float(val):
    if pd.isna(val):
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

def clean_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(val)
    except:
        return 0

def migrate():
    print(f"Starting migration from {EXCEL_FILE} to {DB_FILE}...")
    
    if not os.path.exists(EXCEL_FILE):
        print("Excel file not found!")
        return

    # Initialize Database
    db = Database(DB_FILE)
    
    try:
        xl = pd.ExcelFile(EXCEL_FILE)
        
        # --- 1. Products & Inventory (Sheet: Home) ---
        print("\nMigrating Products & Inventory...")
        df_home = xl.parse("Home")
        
        # Clear existing stock for clean import? 
        # Strategy: upsert products, reset inventory for these items to avoid duplicates if run multiple times
        # For safety in this strict run: just insert.
        
        products_count = 0
        for _, row in df_home.iterrows():
            idx = clean_str(row.get('Index'))
            if not idx: continue
            
            p_id = str(idx) # Ensure string
            name = clean_str(row.get('product'))
            price = clean_float(row.get('unit_price'))
            cost = clean_float(row.get('unit_cost'))
            qty = clean_int(row.get('q_stil'))
            
            # Insert Product
            db.conn.execute("""
                INSERT OR REPLACE INTO products (product_id, name, selling_price, cost_price)
                VALUES (?, ?, ?, ?)
            """, (p_id, name, price, cost))
            
            # Insert Inventory Batch (Initial Stock)
            if qty > 0:
                # Check if batch already exists to prevent duplication on re-run
                batch_check = db.fetch_one("SELECT id FROM inventory WHERE product_id=? AND batch_number='INIT'", (p_id,))
                if not batch_check:
                    db.conn.execute("""
                        INSERT INTO inventory (product_id, quantity, cost_price, batch_number, warehouse_id, received_date)
                        VALUES (?, ?, ?, 'INIT', 1, ?)
                    """, (p_id, qty, cost, datetime.now().date().isoformat()))
            
            products_count += 1
            
        print(f"Processed {products_count} products.")
        db.conn.commit()

        # --- 2. Customers (Sheet: sales) ---
        print("\nMigrating Customers...")
        df_sales = xl.parse("sales")
        
        unique_customers = set()
        if 'customer' in df_sales.columns:
            unique_customers.update(df_sales['customer'].dropna().unique())
            
        # Also check Invoice sheet for customers
        df_inv = xl.parse("invoice")
        if 'customer' in df_inv.columns:
            unique_customers.update(df_inv['customer'].dropna().unique())
            
        cust_map = {} # Name -> ID
        cust_counter = 1000
        
        # Get existing customers to avoid re-creating
        existing = db.fetch_all("SELECT customer_id, name FROM customers")
        for r in existing:
            cust_map[r['name']] = r['customer_id']
            # Update counter to avoid collision
            try:
                cid = int(r['customer_id'])
                if cid > cust_counter: cust_counter = cid
            except: pass
            
        for name in unique_customers:
            clean_name = clean_str(name)
            if not clean_name: continue
            
            if clean_name not in cust_map:
                cust_counter += 1
                new_id = str(cust_counter)
                db.conn.execute("INSERT INTO customers (customer_id, name) VALUES (?, ?)", (new_id, clean_name))
                cust_map[clean_name] = new_id
                
        print(f"Processed {len(unique_customers)} unique customers.")
        db.conn.commit()
        
        # --- 3. Sales Orders (Sheet: sales) ---
        print("\nMigrating Sales Orders...")
        orders_count = 0
        
        for _, row in df_sales.iterrows():
            inv_id = clean_str(row.get('invoice_id'))
            if not inv_id: continue
            
            # Check existence
            chk = db.fetch_one("SELECT order_number FROM sales_orders WHERE order_number=?", (inv_id,))
            if chk: continue # Skip if exists
            
            c_name = clean_str(row.get('customer'))
            c_id = cust_map.get(c_name)
            if not c_id:
                print(f"Warning: Customer {c_name} not found for Invoice {inv_id}")
                continue
                
            date_val = clean_date(row.get('date'))
            total = clean_float(row.get('total'))
            paid = clean_float(row.get('pay'))
            remaining = clean_float(row.get('on_account'))
            
            status = 'completed' if remaining <= 0 else 'partial'
            
            db.conn.execute("""
                INSERT INTO sales_orders (
                    order_number, customer_id, order_date, total_amount, 
                    paid_amount, remaining_amount, status, payment_status
                ) VALUES (?, ?, ?, ?, ?, ?, 'invoiced', ?)
            """, (inv_id, c_id, date_val, total, paid, remaining, status))
            
            orders_count += 1
            
        print(f"Processed {orders_count} sales orders.")
        db.conn.commit()
        
        # --- 4. Sales Items (Sheet: invoice) ---
        print("\nMigrating Sales Items...")
        items_count = 0
        
        # We need to link items to orders.
        # df_inv has 'invoce_id', 'product_id', 'q', 'unit_price'
        
        for _, row in df_inv.iterrows():
            inv_id = clean_str(row.get('invoce_id'))
            if not inv_id: continue
            
            # Check if order exists (we just imported it)
            # If order missing in 'sales' sheet but present here, we create a dummy order?
            # Or skip? Better to skip to maintain integrity, or create a placeholder.
            # Let's check DB.
            ord_chk = db.fetch_one("SELECT order_number FROM sales_orders WHERE order_number=?", (inv_id,))
            if not ord_chk:
                # Create placeholder order?
                # For now, skip and log warning
                # print(f"Skipping item for missing invoice {inv_id}")
                continue

            # Check product existence
            # Some product IDs in Invoice sheet might not match Home sheet Index
            if not p_id:
                print(f"Skipping item with empty product_id for invoice {inv_id}")
                continue
                
            prod_chk = db.fetch_one("SELECT product_id FROM products WHERE product_id=?", (p_id,))
            if not prod_chk:
                print(f"Warning: Product {p_id} not found for Invoice {inv_id}. Skipping item.")
                continue
            
            qty = clean_int(row.get('q'))
            price = clean_float(row.get('unit_price'))
            total = clean_float(row.get('total'))
            
            try:
                db.conn.execute("""
                    INSERT INTO sales_order_items (
                        order_number, product_id, quantity, unit_price, total_price
                    ) VALUES (?, ?, ?, ?, ?)
                """, (inv_id, p_id, qty, price, total))
                items_count += 1
            except sqlite3.Error as e:
                print(f"Error inserting item inv={inv_id} prod={p_id}: {e}")
            
        print(f"Processed {items_count} sales line items.")
        db.conn.commit()

        # --- 5. Payments (Sheet: cach_resive) ---
        print("\nMigrating Payments...")
        pay_count = 0
        
        df_pay = xl.parse("cach_resive")
        for _, row in df_pay.iterrows():
            c_name = clean_str(row.get('customer'))
            amt = clean_float(row.get('amount'))
            date_val = clean_date(row.get('date'))
            
            c_id = cust_map.get(c_name)
            if not c_id: continue
            
            # We don't have a direct link to Invoice ID in this sheet usually, just customer payment.
            # So entity_id = customer_id, entity_type = 'customer_account'?
            # Or try to match with invoice?
            # Strategy: Record as 'general_payment' linked to customer.
            
            db.conn.execute("""
                INSERT INTO payments (
                    payment_type, entity_type, entity_id, amount, payment_date, created_by
                ) VALUES ('income', 'customer', ?, ?, ?, 1)
            """, (c_id, amt, date_val))
            
            pay_count += 1
            
        print(f"Processed {pay_count} payments.")
        db.conn.commit()
        
        print("\nMigration Completed Successfully.")
        
    except Exception as e:
        print(f"\nMIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    migrate()
