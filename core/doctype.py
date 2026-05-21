
"""
Base Document Class
"""
import uuid
import core.frappe as frappe
from core.database import db
import core.database as db_pkg

class Document:
    def __init__(self, doctype: str, name: str = None, **kwargs):
        # Initialize internal storage first to avoid recursion
        super().__setattr__("_data", {})
        
        self.doctype = doctype
        self.meta = frappe.get_meta(doctype)
        self._dirty = False
        self.docstatus = 0
        self.parent = None
        
        if name:
            self._load(name)
        else:
            self.name = kwargs.get("name") or self._generate_name()
            # Populate _data with kwargs
            self._data.update(kwargs)
            self._data['name'] = self.name
            self._data['doctype'] = doctype
            self._data['docstatus'] = 0
            self._dirty = True

    def _generate_name(self):
        # Simplified naming series support
        return str(uuid.uuid4())[:8].upper()

    def _load(self, name):
        """Load document from DB"""
        table = db_pkg.get_table_name(self.doctype)
        res = db.sql(f"SELECT * FROM {table} WHERE name = ?", (name,), as_dict=True)
        if res:
            self._data.update(res[0])
            self.name = self._data['name']
            self.docstatus = self._data.get('docstatus', 0)
            
            # Load Children
            for field in self.meta.get("fields", []):
                if field.get("fieldtype") == "Table":
                    # Fetch keys from child table
                    child_doctype = field['options']
                    child_table = db_pkg.get_table_name(child_doctype)
                    children = db.sql(f"SELECT * FROM {child_table} WHERE parent = ? ORDER BY idx", (self.name,), as_dict=True)
                    self._data[field['fieldname']] = children
        else:
            raise ValueError(f"{self.doctype} {name} not found")

    def __getattr__(self, key):
        if key == "_data":
            return super().__getattribute__("_data")
        return self._data.get(key)
    
    def __setattr__(self, key, value):
        # Attributes stored directly on object - ONLY internal meta
        if key in ["doctype", "meta", "_dirty", "_data", "name"]:
            super().__setattr__(key, value)
        else:
            # Attributes stored in _data (DB fields)
            self._data[key] = value
            self._dirty = True

    def save(self):
        """Upsert document and children"""
        if db.exists(self.doctype, self.name):
            self._update()
        else:
            self._insert()
        
        self.save_children()
        db.commit()
        return self

    def save_children(self):
        # Iterate fields to find Tables
        for field in self.meta.get("fields", []):
            if field.get("fieldtype") == "Table":
                fieldname = field.get("fieldname")
                children = self._data.get(fieldname, [])
                
                child_doctype = field['options']
                child_table = db_pkg.get_table_name(child_doctype)
                
                # Delete existing (Simplified Mode: Delete All and Re-insert)
                # In real ERPNext we track modified
                db.sql(f"DELETE FROM {child_table} WHERE parent = ?", (self.name,))
                
                for idx, child_data in enumerate(children):
                    # Child is a dict usually from UI
                    child_doc = frappe.get_doc(field['options'], **child_data)
                    child_doc.parent = self.name
                    child_doc.parenttype = self.doctype
                    child_doc.parentfield = fieldname
                    child_doc.idx = idx
                    child_doc.save() # Recursion? Child tables are docs too

    def _insert(self):
        # Build INSERT statement dynamically
        valid_fields = [k for k in self._data.keys() if k != 'doctype' and not isinstance(self._data[k], list)]
        placeholders = ", ".join(["?"] * len(valid_fields))
        columns = ", ".join(valid_fields)
        values = [self._data[f] for f in valid_fields]
        
        table = db_pkg.get_table_name(self.doctype)
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        # DEBUG
        # if self.doctype == "Sales Order Item":
        #    print(f"DEBUG INSERT {table}: {query}")
        #    print(f"VALUES: {values}")
            
        db.sql(query, tuple(values), as_dict=False)
        self._dirty = False

    def _update(self):
        # Build UPDATE statement
        updates = []
        values = []
        for k, v in self._data.items():
            if k not in ["name", "doctype"] and not isinstance(v, list):
                updates.append(f"{k} = ?")
                values.append(v)
        
        values.append(self.name)
        table = db_pkg.get_table_name(self.doctype)
        query = f"UPDATE {table} SET {', '.join(updates)} WHERE name = ?"
        db.sql(query, tuple(values), as_dict=False)
        self._dirty = False
        
    def submit(self):
        if self.docstatus == 1:
            return
        self.docstatus = 1
        self.save()
        
    def cancel(self):
        if self.docstatus == 2:
            return
        self.docstatus = 2
        self.save()

    def as_dict(self):
        return self._data
