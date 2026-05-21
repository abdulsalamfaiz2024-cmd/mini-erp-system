"""
Audit Logging Module
Handles recording of all system mutations and key actions.
"""

import json
from datetime import datetime
from typing import Optional, Any
from core.database import get_db, DatabaseError
from core.logger import get_logger

logger = get_logger('security.audit')

class AuditLogger:
    """Manages system audit logs"""
    
    @staticmethod
    def log(user_id: Optional[int], action: str, table_name: str, 
            record_id: Optional[str], old_value: Any = None, new_value: Any = None,
            ip_address: str = '127.0.0.1'):
        """
        Record an audit log entry.
        
        Args:
            user_id: ID of user performing action (None if system)
            action: Type of action (CREATE, UPDATE, DELETE, LOGIN, etc)
            table_name: Affected table or module
            record_id: ID of affected record
            old_value: Previous state (dict or serialization preferred)
            new_value: New state
            ip_address: Request source IP
        """
        try:
            db = get_db()
            
            # Serialize values if they are dicts/objects
            def serialize(val):
                if val is None: return None
                if isinstance(val, (dict, list)):
                    return json.dumps(val, default=str)
                return str(val)

            audit_entry = {
                'user_id': user_id,
                'action': action,
                'table_name': table_name,
                'record_id': record_id,
                'old_value': serialize(old_value),
                'new_value': serialize(new_value),
                'ip_address': ip_address,
                'timestamp': datetime.now()
            }
            
            # Use raw sql insert to avoid circular dependencies or complex ORM logic here
            # We want audit to be fail-safe
            
            columns = ', '.join(audit_entry.keys())
            placeholders = ', '.join(['?' for _ in audit_entry])
            sql = f"INSERT INTO audit_logs ({columns}) VALUES ({placeholders})"
            
            cursor = db.conn.cursor()
            cursor.execute(sql, tuple(audit_entry.values()))
            # We explicitly commit usage log immediately? 
            # Usually audit logs should be part of the transaction OR separate.
            # Mini-ERP: Let's assume part of transaction if inside one, or auto-commit if not.
            # But Database class is autocommit=False usually? No, "isolation_level=None" means autocommit unless BEGIN.
            # So this commits immediately if not in a transaction block.
            
        except Exception as e:
            # Fallback logging if DB fails
            logger.error(f"Failed to write audit log: {e}", exc_info=True)
