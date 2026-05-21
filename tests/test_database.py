"""
Test script to verify database initialization
"""

from core.database import get_db

try:
    # Initialize database
    db = get_db()
    print("[OK] Database initialized successfully")
    
    # Get all tables
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n[OK] Total tables created: {len(tables)}")
    print("\nTables:")
    for table in tables:
        print(f"  - {table}")
    
    # Verify default data
    cursor.execute("SELECT COUNT(*) FROM roles")
    roles_count = cursor.fetchone()[0]
    print(f"\n[OK] Default roles created: {roles_count}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    print(f"[OK] Default users created: {users_count}")
    
    print("\n[OK] Database verification complete!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
