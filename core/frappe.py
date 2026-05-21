
"""
Mini-Frappe Core Module
Mimics the `frappe` namespace from ERPNext.
"""
import os
import json
from core.database import db

# Global Cache
_meta_cache = {}

def get_doc(doctype: str, name: str = None, **kwargs):
    """
    Returns a Document object.
    If a controller exists for the DocType, uses that class instead.
    Usage:
        doc = frappe.get_doc("Customer", "CUST-001")
        doc = frappe.get_doc(doctype="Sales Order", customer="CUST-001", ...) # New doc
    """
    # Try to load controller
    controller_class = get_controller(doctype)
    
    if controller_class:
        if name:
            return controller_class(doctype, name)
        else:
            return controller_class(doctype, **kwargs)
    else:
        # Fall back to base Document
        from core.doctype import Document
        if name:
            return Document(doctype, name)
        else:
            return Document(doctype, **kwargs)

def get_controller(doctype: str):
    """
    Load controller class for a DocType.
    Looks for {doctype}.py in the doctype folder.
    """
    import importlib.util
    
    slug = doctype.replace(" ", "_").lower()
    
    # Search paths
    search_paths = [
        f"d:/sales_systems/apps/selling/doctype/{slug}/{slug}.py",
        f"d:/sales_systems/apps/buying/doctype/{slug}/{slug}.py",
        f"d:/sales_systems/apps/stock/doctype/{slug}/{slug}.py",
        f"d:/sales_systems/apps/accounts/doctype/{slug}/{slug}.py",
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            try:
                # Dynamic import
                spec = importlib.util.spec_from_file_location(slug, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for a class that matches the doctype
                class_name = doctype.replace(" ", "")
                if hasattr(module, class_name):
                    return getattr(module, class_name)
                
                # Also try get_controller function
                if hasattr(module, 'get_controller'):
                    return module.get_controller()
                    
            except Exception as e:
                print(f"Error loading controller for {doctype}: {e}")
                return None
    
    return None


def get_meta(doctype: str):
    """
    Load metadata from JSON file.
    Assumes JSONs are storing in apps/{module}/doctype/{doctype}/{doctype}.json
    or a simplified 'doctypes' folder for now.
    """
    if doctype in _meta_cache:
        return _meta_cache[doctype]
    
    # Simple search in known paths
    # We will assume a flat structure or specific registry for now to keep it simple
    # logic to find the json file
    # For now, let's hardcode a 'doctypes' search path
    search_paths = [
        "d:/sales_systems/core/doctypes",
        "d:/sales_systems/apps/selling/doctype",
        "d:/sales_systems/apps/buying/doctype",
        "d:/sales_systems/apps/stock/doctype",
        "d:/sales_systems/apps/accounts/doctype",
    ]
    
    # Try to find the file
    found_path = None
    slug = doctype.replace(" ", "_").lower()
    
    for path in search_paths:
        # 1. Exact Name Folder
        p1 = os.path.join(path, doctype, f"{doctype}.json")
        # 2. Slug Folder
        p2 = os.path.join(path, slug, f"{slug}.json")
        # 3. Simple File
        p3 = os.path.join(path, f"{doctype}.json")
        # 4. Slug File
        p4 = os.path.join(path, f"{slug}.json")

        if os.path.exists(p1): found_path = p1
        elif os.path.exists(p2): found_path = p2
        elif os.path.exists(p3): found_path = p3
        elif os.path.exists(p4): found_path = p4
        
        if found_path: break
            
    if found_path:
        with open(found_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            _meta_cache[doctype] = meta
            return meta
            
    # Return dummy meta if not found to prevent crash during dev
    return {"fields": []}

def get_list(doctype, *args, **kwargs):
    return db.get_list(doctype, *args, **kwargs)

def get_value(doctype, filters, fieldname="name"):
    return db.get_value(doctype, filters, fieldname)
