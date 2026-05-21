"""
Professional ERPNext-Style Form View
Renders document forms dynamically from DocType metadata.
Fully integrated with backend controllers.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import core.frappe as frappe
from core.database import db


class FormView(ttk.Frame):
    """
    Generic Form View that renders based on DocType metadata.
    Integrated with controllers for proper lifecycle management.
    """
    
    def __init__(self, parent, doctype, name=None, on_back=None):
        super().__init__(parent)
        self.doctype = doctype
        self.doc_name = name
        self.on_back = on_back
        self.controls = {}
        self.child_tables = {}
        
        # Load or create document using controller
        if name:
            self.doc = frappe.get_doc(doctype, name)
            self.is_new = False
        else:
            self.doc = frappe.get_doc(doctype)
            self.is_new = True
        
        self.meta = frappe.get_meta(doctype)
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Build the form interface"""
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=15)
        
        # Back button
        if self.on_back:
            ttk.Button(header, text="< Back", command=self.on_back).pack(side="left")
        
        # Title
        title = f"New {self.doctype}" if self.is_new else f"{self.doctype}: {self.doc_name}"
        ttk.Label(header, text=title, font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        
        # Status indicator
        self.status_label = ttk.Label(header, text="Draft", font=("Segoe UI", 10))
        self.status_label.pack(side="left", padx=10)
        
        # Action buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")
        
        self.save_btn = ttk.Button(btn_frame, text="Save", command=self.save)
        self.save_btn.pack(side="left", padx=5)
        
        self.submit_btn = ttk.Button(btn_frame, text="Submit", command=self.submit)
        self.submit_btn.pack(side="left", padx=5)
        
        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_doc)
        self.cancel_btn.pack(side="left", padx=5)
        
        # Scrollable form area
        canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)
        
        self.form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Build form fields from metadata
        self.build_form()
        self.update_button_states()
    
    def build_form(self):
        """Build form fields from DocType metadata"""
        fields = self.meta.get("fields", [])
        current_section = None
        current_column = None
        row = 0
        col = 0
        
        for field in fields:
            fieldtype = field.get("fieldtype")
            fieldname = field.get("fieldname")
            label = field.get("label", fieldname)
            
            # Skip certain field types
            if fieldtype in ["Section Break", "Column Break", "HTML", "Button"]:
                if fieldtype == "Section Break":
                    # Create section
                    section_frame = ttk.LabelFrame(self.form_frame, text=label or "", padding=10)
                    section_frame.pack(fill="x", pady=10, padx=5)
                    current_section = section_frame
                    row = 0
                    col = 0
                continue
            
            parent = current_section or self.form_frame
            
            if fieldtype == "Table":
                # Child table
                self.create_table_field(parent, field)
            else:
                # Regular field
                self.create_field(parent, field, row, col)
                row += 1
    
    def create_field(self, parent, field, row, col):
        """Create a form field"""
        fieldtype = field.get("fieldtype")
        fieldname = field.get("fieldname")
        label = field.get("label", fieldname)
        options = field.get("options", "")
        
        # Container
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill="x", pady=5, padx=5)
        
        # Label
        ttk.Label(field_frame, text=label, width=20, anchor="e").pack(side="left", padx=5)
        
        # Input based on type
        var = tk.StringVar()
        
        if fieldtype == "Select":
            opts = options.split("\n") if options else []
            widget = ttk.Combobox(field_frame, textvariable=var, values=opts, width=40)
        elif fieldtype == "Link":
            # Link field with lookup
            widget = ttk.Entry(field_frame, textvariable=var, width=42)
            # Could add lookup button here
        elif fieldtype == "Text" or fieldtype == "Small Text":
            widget = tk.Text(field_frame, height=3, width=42)
            widget.var = None  # Text widget doesn't use var
        elif fieldtype == "Check":
            var = tk.BooleanVar()
            widget = ttk.Checkbutton(field_frame, variable=var)
        elif fieldtype in ["Currency", "Float", "Int"]:
            widget = ttk.Entry(field_frame, textvariable=var, width=42)
        else:
            # Default to entry
            widget = ttk.Entry(field_frame, textvariable=var, width=42)
        
        widget.pack(side="left", padx=5, fill="x", expand=True)
        
        self.controls[fieldname] = {"widget": widget, "var": var, "fieldtype": fieldtype}
    
    def create_table_field(self, parent, field):
        """Create a child table field"""
        fieldname = field.get("fieldname")
        label = field.get("label", fieldname)
        child_doctype = field.get("options")
        
        # Table container
        table_frame = ttk.LabelFrame(parent, text=label, padding=10)
        table_frame.pack(fill="both", expand=True, pady=10, padx=5)
        
        # Get child meta
        child_meta = frappe.get_meta(child_doctype)
        child_fields = child_meta.get("fields", [])
        
        # Filter to displayable fields
        display_fields = [f for f in child_fields if f.get("fieldtype") in 
                         ["Data", "Link", "Int", "Float", "Currency", "Select"]][:5]
        
        columns = [f.get("fieldname") for f in display_fields]
        headers = [f.get("label", f.get("fieldname")) for f in display_fields]
        
        # Treeview for table
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        for col, header in zip(columns, headers):
            tree.heading(col, text=header)
            tree.column(col, width=120)
        
        tree.pack(fill="both", expand=True)
        
        # Add/Remove buttons
        btn_frame = ttk.Frame(table_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="+ Add Row", 
                   command=lambda: self.add_table_row(fieldname, tree, display_fields)).pack(side="left")
        ttk.Button(btn_frame, text="- Remove Row",
                   command=lambda: self.remove_table_row(tree)).pack(side="left", padx=5)
        
        self.child_tables[fieldname] = {
            "tree": tree,
            "fields": display_fields,
            "doctype": child_doctype
        }
    
    def add_table_row(self, fieldname, tree, fields):
        """Add a row to child table"""
        # Open a dialog to enter values
        dialog = tk.Toplevel(self)
        dialog.title("Add Row")
        dialog.geometry("400x300")
        
        entries = {}
        for i, field in enumerate(fields):
            fname = field.get("fieldname")
            label = field.get("label", fname)
            
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            var = tk.StringVar()
            entry = ttk.Entry(dialog, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[fname] = var
        
        def save_row():
            values = [entries[f.get("fieldname")].get() for f in fields]
            tree.insert("", "end", values=values)
            dialog.destroy()
        
        ttk.Button(dialog, text="Add", command=save_row).grid(row=len(fields), column=1, pady=20)
    
    def remove_table_row(self, tree):
        """Remove selected row from child table"""
        selected = tree.selection()
        if selected:
            tree.delete(selected[0])
    
    def load_data(self):
        """Load document data into form"""
        # Update status
        docstatus = self.doc._data.get('docstatus', 0)
        status = self.doc._data.get('status', 'Draft')
        self.status_label.config(text=f"[{status}]")
        
        # Load regular fields
        for fieldname, control in self.controls.items():
            value = self.doc._data.get(fieldname, "")
            widget = control["widget"]
            var = control["var"]
            fieldtype = control["fieldtype"]
            
            if fieldtype in ["Text", "Small Text"]:
                widget.delete("1.0", "end")
                widget.insert("1.0", str(value or ""))
            elif fieldtype == "Check":
                var.set(bool(value))
            else:
                var.set(str(value or ""))
        
        # Load child tables
        for fieldname, table_info in self.child_tables.items():
            tree = table_info["tree"]
            fields = table_info["fields"]
            
            # Clear existing
            for item in tree.get_children():
                tree.delete(item)
            
            # Load rows
            children = self.doc._data.get(fieldname, [])
            for child in children:
                values = [child.get(f.get("fieldname"), "") for f in fields]
                tree.insert("", "end", values=values)
        
        self.update_button_states()
    
    def update_button_states(self):
        """Update button visibility based on docstatus"""
        docstatus = self.doc._data.get('docstatus', 0)
        
        if docstatus == 0:  # Draft
            self.save_btn.config(state="normal")
            self.submit_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
        elif docstatus == 1:  # Submitted
            self.save_btn.config(state="disabled")
            self.submit_btn.config(state="disabled")
            self.cancel_btn.config(state="normal")
        else:  # Cancelled
            self.save_btn.config(state="disabled")
            self.submit_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
    
    def collect_data(self):
        """Collect form data into document"""
        # Regular fields
        for fieldname, control in self.controls.items():
            widget = control["widget"]
            var = control["var"]
            fieldtype = control["fieldtype"]
            
            if fieldtype in ["Text", "Small Text"]:
                value = widget.get("1.0", "end-1c")
            elif fieldtype == "Check":
                value = 1 if var.get() else 0
            else:
                value = var.get()
            
            self.doc._data[fieldname] = value
        
        # Child tables
        for fieldname, table_info in self.child_tables.items():
            tree = table_info["tree"]
            fields = table_info["fields"]
            
            children = []
            for item in tree.get_children():
                values = tree.item(item)["values"]
                child_data = {}
                for i, field in enumerate(fields):
                    fname = field.get("fieldname")
                    child_data[fname] = values[i] if i < len(values) else ""
                children.append(child_data)
            
            self.doc._data[fieldname] = children
    
    def save(self):
        """Save the document"""
        try:
            self.collect_data()
            self.doc.save()
            messagebox.showinfo("Success", f"Saved {self.doctype}: {self.doc.name}")
            self.doc_name = self.doc.name
            self.is_new = False
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def submit(self):
        """Submit the document"""
        try:
            if self.is_new:
                self.save()
            
            self.collect_data()
            self.doc.submit()
            messagebox.showinfo("Success", f"Submitted {self.doctype}: {self.doc.name}")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def cancel_doc(self):
        """Cancel the document"""
        try:
            if messagebox.askyesno("Confirm", f"Cancel {self.doctype}: {self.doc.name}?"):
                self.doc.cancel()
                messagebox.showinfo("Success", f"Cancelled {self.doctype}: {self.doc.name}")
                self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
