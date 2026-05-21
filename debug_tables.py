import sys
import os
sys.path.append(os.getcwd())
try:
    from core.database import get_db
except ImportError:
    # Fallback if run from different dir
    sys.path.append(r'd:\sales_systems')
    from core.database import get_db

db = get_db()
print(f"DB Path: {db.db_path}")

print("\n--- Tables ---")
try:
    tables = db.sql("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    table_names = [dict(t)['name'] for t in tables]
    for t in table_names:
        print(t)
except Exception as e:
    print(f"Error listing tables: {e}")

print("\n--- Row Counts ---")
check_list = ['customers', 'tabCustomer', 'products', 'tabProduct', 'items', 'tabItem', 'suppliers', 'tabSupplier']
for t in check_list:
    try:
        cnt = db.sql(f"SELECT count(*) as c FROM {t}")[0]['c']
        print(f"{t}: {cnt}")
    except:
        print(f"{t}: MISSING")
