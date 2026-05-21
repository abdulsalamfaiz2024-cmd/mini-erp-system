"""
Test script for Security Module
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from modules.security.auth import AuthManager
from modules.security.rbac import RBAC
from modules.security.audit import AuditLogger
from core.database import get_db

def test_security():
    print("Testing Security Module...")
    db = get_db()
    
    # 1. Test User Creation
    print("\n1. Testing User Creation...")
    try:
        # Create a test role first if needed, but 'user' role (id=3) should exist from db init
        success = AuthManager.create_user(
            username="testuser",
            password="password123",
            full_name="Test User",
            role_id=3, # user role
            created_by=1 # admin
        )
        if success:
            print("[OK] User 'testuser' created")
        else:
            print("[WARN] Failed to create user (might already exist)")
            
    except Exception as e:
        print(f"[ERROR] User creation failed: {e}")

    # 2. Test Login
    print("\n2. Testing Login...")
    try:
        # Success case
        success, msg, user_data = AuthManager.login("testuser", "password123")
        if success:
            print(f"[OK] Login successful for {user_data['username']}")
            # Verify session/user data
            assert user_data['role_id'] == 3
        else:
            print(f"[FAIL] Login failed: {msg}")
            
        # Failure case
        success, msg, _ = AuthManager.login("testuser", "wrongpassword")
        if not success:
            print("[OK] Login failed correctly for wrong password")
        else:
            print("[FAIL] Login succeeded with wrong password")
            
    except Exception as e:
         print(f"[ERROR] Login test failed: {e}")

    # 3. Test RBAC
    print("\n3. Testing RBAC...")
    try:
        # Admin (Role 1) should have 'all' permission
        is_allowed = RBAC.check_permission(1, 'sales', 'delete')
        if is_allowed:
            print("[OK] Admin has delete permission on sales")
        else:
            print("[FAIL] Admin denied delete permission")
            
        # User (Role 3) should have read but not delete on sales (based on default data in db.py)
        # Default user permissions: {"sales": ["create", "read"], ...}
        
        can_read = RBAC.check_permission(3, 'sales', 'read')
        if can_read:
             print("[OK] User has read permission on sales")
        else:
             print("[FAIL] User denied read permission")

        can_delete = RBAC.check_permission(3, 'sales', 'delete')
        if not can_delete:
             print("[OK] User correctly denied delete permission on sales")
        else:
             print("[FAIL] User allowed to delete sales (Should be denied)")
             
    except Exception as e:
        print(f"[ERROR] RBAC test failed: {e}")

    # 4. Test Audit Log
    print("\n4. Testing Audit Log...")
    try:
        # Check if LOGIN action from step 2 was logged
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE action = 'LOGIN' AND user_id = (SELECT id FROM users WHERE username='testuser') ORDER BY id DESC LIMIT 1")
        log = cursor.fetchone()
        if log:
            print(f"[OK] Audit log found for login: {log['timestamp']}")
        else:
            print("[FAIL] No audit log found for login")
            
    except Exception as e:
        print(f"[ERROR] Audit log test failed: {e}")

if __name__ == "__main__":
    test_security()
