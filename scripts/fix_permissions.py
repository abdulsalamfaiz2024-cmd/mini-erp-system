import sys
import os

sys.path.insert(0, os.getcwd())

from core.database import get_db

def fix_perms():
    print("Promoting Users to Fix Permission Errors...")
    db = get_db()
    
    # 1. Promote John Doe (Likely User 1) to Admin (Level 5)
    db.execute("UPDATE employees SET approval_level=5 WHERE full_name LIKE 'John Doe%'")
    print("  Promoted John Doe to Level 5 (Admin)")
    
    # 2. Promote Jane Doe to Finance/Warehouse (Level 3)
    db.execute("UPDATE employees SET approval_level=3 WHERE full_name LIKE 'Jane Doe%'")
    print("  Promoted Jane Doe to Level 3")
    
    # Validate
    rows = db.fetch_all("SELECT full_name, approval_level FROM employees WHERE full_name LIKE 'John%' OR full_name LIKE 'Jane%'")
    print("  Current Levels:", [dict(r) for r in rows])

if __name__ == "__main__":
    fix_perms()
