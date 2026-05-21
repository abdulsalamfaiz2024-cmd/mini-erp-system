"""
Role-Based Access Control (RBAC) Module
Handles permission checks and role management.
"""

import json
from typing import List, Dict, Union
from core.database import get_db
from core.logger import get_logger

logger = get_logger('security.rbac')

class RBAC:
    """Manages Role-Based Access Control"""
    
    _permissions_cache = {}

    @classmethod
    def get_role_permissions(cls, role_id: int) -> Dict:
        """Fetch and cache permissions for a role"""
        if role_id in cls._permissions_cache:
            return cls._permissions_cache[role_id]
        
        try:
            db = get_db()
            row = db.fetch_one("SELECT permissions_json FROM roles WHERE id = ?", (role_id,))
            
            if row and row['permissions_json']:
                perms = json.loads(row['permissions_json'])
                cls._permissions_cache[role_id] = perms
                return perms
            return {}
            
        except Exception as e:
            logger.error(f"Failed to load permissions for role {role_id}: {e}")
            return {}

    @classmethod
    def check_permission(cls, role_id: int, module: str, action: str) -> bool:
        """
        Check if a role has permission to perform an action on a module.
        
        Args:
            role_id: User's role ID
            module: Target module (sales, inventory, etc)
            action: Action type (create, read, update, delete, etc)
        """
        if role_id is None:
            return False
            
        perms = cls.get_role_permissions(role_id)
        
        # Super admin check
        if perms.get('all') is True:
            return True
            
        # Module level check
        module_perms = perms.get(module)
        if not module_perms:
            return False
            
        if module_perms is True: # Full access to module
            return True
            
        if isinstance(module_perms, list):
            return action in module_perms or 'all' in module_perms
            
        return False

    @staticmethod
    def require_permission(module: str, action: str):
        """Decorator for checking permissions (placeholder for UI/Service layer)"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # This would need context of 'current_user'
                # For now, just a stub logic showing where it belongs
                return func(*args, **kwargs)
            return wrapper
        return decorator
