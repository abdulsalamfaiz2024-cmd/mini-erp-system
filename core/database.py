
import sqlite3
import threading
import json
from typing import List, Dict, Any, Optional

class Database:
    """
    Singleton Database Wrapper using SQLite.
    Mimics `frappe.db` methods.
    """
    _instance = None
    _local = threading.local()

    def __new__(cls, db_path="sales_system.db"):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_path = db_path
        return cls._instance

    def connect(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def commit(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.commit()

    def rollback(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.rollback()

    def sql(self, query: str, values: tuple = (), as_dict: bool = True) -> List[Dict[str, Any]]:
        """Run SQL query"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, values)
            if query.lower().strip().startswith(('select', 'pragma')):
                rows = cursor.fetchall()
                if as_dict:
                    return [dict(row) for row in rows]
                return rows
            else:
                self.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"SQL Error: {e} | Query: {query}")
            raise e

    def get_value(self, doctype: str, filters: Dict[str, Any], fieldname: str = "name") -> Any:
        """Get a single value from the database"""
        # Construct simple WHERE clause
        conditions = []
        values = []
        for key, val in filters.items():
            conditions.append(f"{key} = ?")
            values.append(val)
        
        where_clause = " AND ".join(conditions)
        table = get_table_name(doctype)
        query = f"SELECT {fieldname} FROM {table} WHERE {where_clause} LIMIT 1"
        
        result = self.sql(query, tuple(values), as_dict=True)
        if result:
            return result[0].get(fieldname)
        return None

    def get_list(self, doctype: str, filters: Dict[str, Any] = None, fields: List[str] = None):
        """Get list of records"""
        fields_str = ", ".join(fields) if fields else "*"
        table = get_table_name(doctype)
        query = f"SELECT {fields_str} FROM {table}"
        
        values = []
        if filters:
            conditions = []
            for key, val in filters.items():
                if isinstance(val, (list, tuple)) and list(val)[0] == "like":
                    conditions.append(f"{key} LIKE ?")
                    values.append(val[1])
                else:
                    conditions.append(f"{key} = ?")
                    values.append(val)
            query += " WHERE " + " AND ".join(conditions)
            
        return self.sql(query, tuple(values))

    def exists(self, doctype: str, name: str) -> bool:
        return bool(self.get_value(doctype, {"name": name}, "name"))
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Alias for sql() for compatibility"""
        return self.sql(query, params, as_dict=True)
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch single row"""
        results = self.sql(query, params, as_dict=True)
        return results[0] if results else None
    
    def insert(self, table: str, data: Dict, return_id: bool = True):
        """Insert a row into a table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.sql(query, values)
    
    def update(self, table: str, data: Dict, where: str, where_params: tuple):
        """Update rows in a table"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        values = tuple(data.values()) + where_params
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        return self.sql(query, values)
    
    @property
    def conn(self):
        """Get the current connection"""
        return self.connect()
    
    def transaction(self):
        """Context manager for transactions"""
        return DatabaseTransaction(self)


class DatabaseTransaction:
    """Context manager for database transactions"""
    def __init__(self, db: Database):
        self.db = db
    
    def __enter__(self):
        return self.db.connect().cursor()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()
        return False


class DatabaseError(Exception):
    """Custom database error"""
    pass


def get_table_name(doctype: str) -> str:
    # Standardize table name: tab + snake_case
    slug = doctype.replace(" ", "_").lower()
    return f"tab{slug}"


# Global instance
db = Database()


def get_db() -> Database:
    """Get the singleton database instance"""
    return db


def close_db():
    """Close database connections"""
    if hasattr(db._local, 'conn'):
        db._local.conn.close()
        delattr(db._local, 'conn')

