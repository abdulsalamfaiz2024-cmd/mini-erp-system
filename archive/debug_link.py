import sys
import os

# Ensure unicode printing
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.getcwd())
from core.database import get_db

def check():
    db = get_db()
    users = db.fetch_all("SELECT id, username, full_name FROM users")
    print(f"Users found: {len(users)}")
    for u in users:
        print(f"User: ID={u['id']}, Name={u['username']}")
        
    employees = db.fetch_all("SELECT employee_id, full_name, user_id FROM employees")
    print(f"Employees found: {len(employees)}")
    for e in employees:
        print(f"Employee: ID={e['employee_id']}, Link_User_ID={e['user_id']}, Name={e['full_name']}")
        
    # Check Admin Link specifically
    admin = next((u for u in users if u['username'] == 'admin'), None)
    if admin:
        link = next((e for e in employees if e['user_id'] == admin['id']), None)
        if link:
            print(f"SUCCESS: Admin (ID {admin['id']}) is linked to Employee {link['employee_id']}")
        else:
            print(f"FAILURE: Admin (ID {admin['id']}) has NO Employee record!")
            
            # Auto-Fix
            print("Attempting Auto-Fix...")
            import uuid
            try:
                emp_id = str(uuid.uuid4())
                db.insert('employees', {
                    'employee_id': emp_id,
                    'full_name': 'System Admin',
                    'job_title': 'Administrator',
                    'department': 'IT',
                    'status': 'ACTIVE',
                    'user_id': admin['id'],
                    'can_create_orders': 1,
                    'can_approve_orders': 1,
                    'can_release_inventory': 1,
                    'can_post_accounting': 1
                })
                print(f"FIXED: Created Admin Employee {emp_id}")
            except Exception as e:
                print(f"Fix Failed: {e}")

if __name__ == "__main__":
    check()
