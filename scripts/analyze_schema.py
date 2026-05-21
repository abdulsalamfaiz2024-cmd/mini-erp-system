"""
Database Schema Analyzer
Compares old and new database schemas to find matching columns.
"""
import sqlite3

def get_tables_and_columns(db_path):
    """Get all tables and their columns from a database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        schema[table] = [col[1] for col in columns]  # col[1] is column name
    
    conn.close()
    return schema

def analyze_schemas():
    """Compare old and new database schemas"""
    
    print("=" * 60)
    print("DATABASE SCHEMA ANALYSIS")
    print("=" * 60)
    
    # Analyze current (new) database
    print("\n>>> CURRENT DATABASE: perfect_sales_system.db")
    try:
        new_schema = get_tables_and_columns("perfect_sales_system.db")
        print(f"Tables found: {len(new_schema)}")
        for table, columns in sorted(new_schema.items()):
            print(f"\n  {table}:")
            print(f"    Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
    except Exception as e:
        print(f"Error: {e}")
        new_schema = {}
    
    # Analyze old database
    print("\n>>> OLD DATABASE: sales_system.db")
    try:
        old_schema = get_tables_and_columns("sales_system.db")
        print(f"Tables found: {len(old_schema)}")
        for table, columns in sorted(old_schema.items()):
            print(f"\n  {table}:")
            print(f"    Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
    except Exception as e:
        print(f"Error: {e}")
        old_schema = {}
    
    # Find matching tables
    print("\n" + "=" * 60)
    print("MATCHING TABLES")
    print("=" * 60)
    
    matching = []
    for old_table in old_schema:
        for new_table in new_schema:
            # Check for exact match or similar names
            if old_table.lower() == new_table.lower():
                old_cols = set(old_schema[old_table])
                new_cols = set(new_schema[new_table])
                common = old_cols & new_cols
                matching.append({
                    "old_table": old_table,
                    "new_table": new_table,
                    "common_columns": list(common),
                    "old_only": list(old_cols - new_cols),
                    "new_only": list(new_cols - old_cols)
                })
    
    for m in matching:
        print(f"\nTable: {m['old_table']} -> {m['new_table']}")
        print(f"  Common columns ({len(m['common_columns'])}): {m['common_columns']}")
        print(f"  Old only: {m['old_only'][:5]}{'...' if len(m['old_only']) > 5 else ''}")
        print(f"  New only: {m['new_only'][:5]}{'...' if len(m['new_only']) > 5 else ''}")
    
    # Check for key tables
    print("\n" + "=" * 60)
    print("KEY DATA TABLES CHECK")
    print("=" * 60)
    
    key_tables = ["products", "customers", "items", "customer", "item", "sales", "orders"]
    
    for key in key_tables:
        old_matches = [t for t in old_schema if key.lower() in t.lower()]
        new_matches = [t for t in new_schema if key.lower() in t.lower()]
        if old_matches or new_matches:
            print(f"\n'{key}':")
            print(f"  Old DB: {old_matches}")
            print(f"  New DB: {new_matches}")

if __name__ == "__main__":
    analyze_schemas()
