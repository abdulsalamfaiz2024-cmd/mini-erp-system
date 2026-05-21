import sys
import os
sys.path.append(os.getcwd())
try:
    from core.database import get_db
except ImportError:
    sys.path.append(r'd:\sales_systems')
    from core.database import get_db

db = get_db()

print("--- tabItem Columns ---")
try:
    cols = db.sql("PRAGMA table_info(tabItem)")
    for c in cols:
        print(f"{c['name']} ({c['type']})")
except Exception as e:
    print(e)

print("\n--- tabSales Order Item Columns ---")
try:
    cols = db.sql("PRAGMA table_info('tabSales Order Item')")
    # If table name has spaces, it needs quotes. Or maybe it is tabSales_Order_Item?
    # Schema utils usually replace spaces with underscores.
    if not cols:
         cols = db.sql("PRAGMA table_info(tabSales_Order_Item)")
         
    for c in cols:
        print(f"{c['name']} ({c['type']})")
except Exception as e:
    print(e)

print("\n--- tabSupplier Columns ---")
try:
    cols = db.sql("PRAGMA table_info(tabSupplier)")
    for c in cols:
        print(f"{c['name']} ({c['type']})")
except Exception as e:
    print(e)
