
import tkinter as tk
from tkinter import ttk
from ui.framework.desk_styles import Theme as DeskTheme

class BaseControl(tk.Frame):
    def __init__(self, parent, field_def, on_change=None):
        super().__init__(parent, bg="white")
        self.field_def = field_def
        self.on_change = on_change
        self.value = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Label
        self.lbl = ttk.Label(
            self, 
            text=self.field_def.get("label", self.field_def.get("fieldname")), 
            font=("Inter", 9),
            foreground=DeskTheme.TEXT_MUTED,
            background="white"
        )
        self.lbl.pack(anchor="w", pady=(0, 2))
        
        # Input Widget (Override)
        self.render_input()
        
    def render_input(self):
        pass
        
    def get_value(self):
        return self.value
        
    def set_value(self, val):
        self.value = val

class DataControl(BaseControl):
    def render_input(self):
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var)
        self.entry.pack(fill="x", ipady=5)
        
        if self.on_change:
            self.var.trace("w", lambda *args: self.on_change(self.field_def["fieldname"], self.var.get()))

    def set_value(self, val):
        self.var.set(val or "")

class SelectControl(BaseControl):
    def render_input(self):
        options = self.field_def.get("options", "").split("\n")
        self.var = tk.StringVar(value=options[0] if options else "")
        self.combo = ttk.Combobox(self, textvariable=self.var, values=options, state="readonly")
        self.combo.pack(fill="x", ipady=5)
        
    def set_value(self, val):
        self.var.set(val or "")

class LinkControl(BaseControl):
    """
    Enhanced Link field control with SmartLookupField.
    Provides autocomplete, dropdown selection, and bi-directional binding.
    Uses LookupService to fetch data based on the linked DocType (options).
    """
    
    def render_input(self):
        # Get the linked DocType from field options
        linked_doctype = self.field_def.get("options", "")
        
        # Create variables for ID and display name
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        
        # Get the appropriate data source
        data_source = self._get_data_source(linked_doctype)
        
        if data_source:
            # Use SmartLookupField for supported DocTypes
            try:
                from ui.widgets.smart_lookup import SmartLookupField
                
                self.lookup = SmartLookupField(
                    self,
                    label="",  # Label already shown by BaseControl
                    data_source=data_source,
                    id_var=self.id_var,
                    name_var=self.name_var,
                    on_select=self._on_select,
                    placeholder=f"Search {linked_doctype}..."
                )
                self.lookup.pack(fill="x")
                
            except ImportError:
                # Fallback to basic entry if SmartLookupField not available
                self._render_basic_entry()
        else:
            # Fallback to basic entry for unknown DocTypes
            self._render_basic_entry()
    
    def _render_basic_entry(self):
        """Fallback to basic entry field"""
        self.id_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.id_var)
        self.entry.pack(fill="x", ipady=5)
        
    def _get_data_source(self, doctype):
        """Get the data source function for a DocType"""
        try:
            from modules.lookup_service import LookupService
            return LookupService.get_data_source(doctype)
        except ImportError:
            return None
    
    def _on_select(self, item_id, item_name, extra_data):
        """Callback when an item is selected"""
        if self.on_change:
            self.on_change(self.field_def["fieldname"], item_id)
        
    def get_value(self):
        """Return the selected ID"""
        return self.id_var.get()
        
    def set_value(self, val):
        """Set the field value"""
        if hasattr(self, 'lookup'):
            # Use SmartLookupField's set method
            self.lookup.set_value(item_id=val or "")
        else:
            self.id_var.set(val or "")


class TableControl(BaseControl):
    def render_input(self):
        # Frame for table
        self.frame = tk.Frame(self, bg="white", borderwidth=1, relief="solid")
        self.frame.pack(fill="x", pady=5)
        
        # Columns (Simplified: just Name + 2 data fields from child doc)
        options = self.field_def.get("options") # e.g. "Sales Order Item"
        self.child_doctype = options
        
        # We need child meta to know columns
        try:
            self.child_meta = frappe.get_meta(options)
            self.cols = [f.get("fieldname") for f in self.child_meta.get("fields", []) if f.get("fieldtype") in ["Data", "Int", "Float", "Currency", "Link"]][:4]
        except:
            self.cols = ["name"]
            
        # Headers
        header_frame = tk.Frame(self.frame, bg="#f8f9fa")
        header_frame.pack(fill="x")
        for c in self.cols:
            tk.Label(header_frame, text=c, width=15, bg="#f8f9fa").pack(side="left", padx=1)
            
        self.rows_frame = tk.Frame(self.frame, bg="white")
        self.rows_frame.pack(fill="x")
        
        # Add Row Button
        ttk.Button(self, text="+ Add Row", command=self.add_row, style="Primary.TButton").pack(anchor="w", pady=5)
        
        self.rows = []

    def set_value(self, val):
        # val should be a list of dicts (children)
        # Clear existing
        for r in self.rows:
            r.destroy()
        self.rows = []
        
        if not val:
            return

        for row_data in val:
            self.render_row(row_data)

    def add_row(self):
        # Create empty row data
        row_data = {"doctype": self.child_doctype}
        # In real app, we'd add this to the parent doc's list
        self.render_row(row_data)
        
        # Notify change? Complex for table
        
    def render_row(self, row_data):
        row = tk.Frame(self.rows_frame, bg="white")
        row.pack(fill="x", pady=1)
        self.rows.append(row)
        
        for c in self.cols:
            # Editable entries for each cell
            var = tk.StringVar(value=row_data.get(c, ""))
            e = ttk.Entry(row, textvariable=var, width=15)
            e.pack(side="left", padx=1)
            # Bind updates logic here... avoiding for speed

CONTROL_MAP = {
    "Data": DataControl,
    "Select": SelectControl,
    "Link": LinkControl,
    "Int": DataControl,
    "Float": DataControl,
    "Currency": DataControl,
    "Date": DataControl,
    "Table": TableControl
}

def get_control(parent, field_def, on_change=None):
    ftype = field_def.get("fieldtype", "Data")
    cls = CONTROL_MAP.get(ftype, DataControl)
    return cls(parent, field_def, on_change)
