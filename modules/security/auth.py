"""
Authentication Module
Handles user login, session management, and password security.
Uses standard hashlib for dependency-free secure hashing.
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from core.database import get_db
from core.logger import get_logger
from modules.security.audit import AuditLogger

logger = get_logger('security.auth')

class AuthManager:
    """Manages user authentication and sessions"""
    
    # Simple session store (Token -> UserID)
    # In production, this might be Redis or DB table.
    # For Mini-ERP, in-memory is okay per session, but DB is better for persistence.
    # We will verify if we need persistent sessions. Implementation plan said "Add session management".
    # Implementation plan implies simple session.
    _active_sessions = {} 

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> str:
        """Hash password using PBKDF2"""
        if salt is None:
            salt = os.urandom(32)
        
        # PBKDF2-HMAC-SHA256
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000 # Iterations
        )
        # Store as salt$hash hex string
        return f"{salt.hex()}${key.hex()}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt_hex, key_hex = stored_hash.split('$')
            salt = bytes.fromhex(salt_hex)
            
            new_key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt,
                100000
            )
            return secrets.compare_digest(new_key.hex(), key_hex)
        except Exception:
            return False

    @classmethod
    def login(cls, username: str, password: str) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Attempt login.
        Returns: (Success, Message, UserData)
        """
        db = get_db()
        try:
            # user query
            user = db.fetch_one(
                "SELECT id, username, password_hash, full_name, role_id, is_active FROM users WHERE username = ?", 
                (username,)
            )
            
            if not user:
                return False, "Invalid username or password", None
                
            if not user['is_active']:
                return False, "Account is disabled", None
                
            # Verify password
            if cls.verify_password(password, user['password_hash']):
                # Record login
                AuditLogger.log(user['id'], 'LOGIN', 'users', str(user['id']), ip_address='local')
                
                # Update last login
                db.update('users', {'last_login': datetime.now()}, 'id = ?', (user['id'],))
                
                # Create session (simple dict return for now)
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role_id': user['role_id']
                }
                
                # Enforce Employee Link for Approval Level
                emp = db.fetch_one("SELECT approval_level FROM employees WHERE user_id = ?", (user['id'],))
                if emp:
                    user_data['approval_level'] = emp['approval_level']
                else:
                    user_data['approval_level'] = 0
                
                # Could generate token here if needing stateless auth
                return True, "Login successful", user_data
            else:
                AuditLogger.log(None, 'LOGIN_FAILED', 'users', username, new_value='Wrong Password')
                return False, "Invalid username or password", None
                
        except Exception as e:
            logger.error(f"Login error for {username}: {e}", exc_info=True)
            return False, "System error during login", None

    @classmethod
    def create_user(cls, username: str, password: str, full_name: str, role_id: int, created_by: int) -> bool:
        """Create a new user"""
        db = get_db()
        try:
            password_hash = cls.hash_password(password)
            
            user_id = db.insert('users', {
                'username': username,
                'password_hash': password_hash,
                'full_name': full_name,
                'role_id': role_id,
                'is_active': 1
            })
            
            AuditLogger.log(created_by, 'CREATE_USER', 'users', str(user_id), new_value=username)
            return True
        except Exception as e:
            logger.error(f"Failed to create user {username}: {e}")
            return False
