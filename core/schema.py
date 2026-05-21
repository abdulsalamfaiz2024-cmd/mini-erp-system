
"""
Schema Sync Utils
Creates/Updates tables based on DocType JSON.
"""
from core.database import db
import core.frappe as frappe

TYPE_MAP = {
    "Data": "TEXT",
    "Select": "TEXT",
    "Link": "TEXT",
    "Int": "INTEGER",
    "Currency": "REAL",
    "Float": "REAL",
    "Check": "INTEGER",
    "Text": "TEXT",
    "Small Text": "TEXT",
    "Long Text": "TEXT",
    "Code": "TEXT",
    "HTML": "TEXT",
    "Date": "TEXT",
    "Datetime": "TEXT",
    "Time": "TEXT"
}

def sync_doctype(doctype):
    """
    Creates or Updates table for DocType
    """
    meta = frappe.get_meta(doctype)
    table_name = f"tab{doctype}"
    
    # Standard columns
    columns = [
        "name TEXT PRIMARY KEY",
        "creation TEXT",
        "modified TEXT",
        "modified_by TEXT",
        "owner TEXT",
        "docstatus INTEGER DEFAULT 0",
        "parent TEXT",
        "parentfield TEXT",
        "parenttype TEXT",
        "idx INTEGER"
    ]
    
    # Field columns
    for field in meta.get("fields", []):
        if field.get("fieldtype") in ["Section Break", "Column Break", "HTML", "Button", "Table"]:
            continue
            
        fname = field.get("fieldname")
        ftype = TYPE_MAP.get(field.get("fieldtype"), "TEXT")
        columns.append(f"{fname} {ftype}")
    
    # Check if table exists
    result = db.sql(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'", as_dict=True)
    
    if not result:
        # Create
        query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
        db.sql(query)
        print(f"Created table {table_name}")
    else:
        # Update (Simplified: Add missing columns)
        # In a real scenario we'd check each column
        current_cols_info = db.sql(f"PRAGMA table_info({table_name})", as_dict=True)
        current_cols = [c['name'] for c in current_cols_info]
        
        for col_def in columns:
            col_name = col_def.split(" ")[0]
            if col_name not in current_cols:
                try:
                    db.sql(f"ALTER TABLE {table_name} ADD COLUMN {col_def}")
                    print(f"Added column {col_name} to {table_name}")
                except Exception as e:
                    print(f"Failed to add column {col_name}: {e}")

def sync_all_doctypes():
    """Sync all DocTypes found in apps directory"""
    import os
    root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps")
    
    print(f"Scanning for DocTypes in {root_dir}...")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(".json"):
                doctype = f.replace(".json", "")
                try:
                    frappe.get_meta(doctype)
                    sync_doctype(doctype)
                except Exception as e:
                    print(f"Skipping {f}: {e}")

if __name__ == "__main__":
    sync_all_doctypes()

