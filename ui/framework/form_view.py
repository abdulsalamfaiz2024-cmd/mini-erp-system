"""
Professional ERPNext-Style Form View
Renders document forms dynamically from DocType metadata.
Fully integrated with backend controllers.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import core.frappe as frappe
from core.database import db
from ui.framework.desk_styles import Theme
from ui.widgets.smart_lookup import SmartLookupField
from modules.lookup_service import LookupService



class FormView(ttk.Frame):
    """
    Generic Form View that renders based on DocType metadata.
    All buttons connected to backend controllers.
    """
    
    def __init__(self, parent, doctype, name=None, on_back=None):
        super().__init__(parent, style="Content.TFrame")
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
        # Header bar
        header = tk.Frame(self, bg=Theme.BG_WHITE)
        header.pack(fill="x", padx=25, pady=20)
        
        # Left side - Back and title
        left_frame = tk.Frame(header, bg=Theme.BG_WHITE)
        left_frame.pack(side="left", fill="y")
        
        # Back button
        if self.on_back:
            back_btn = tk.Button(left_frame, text="← Back",
                                font=(Theme.FONT_FAMILY, 10),
                                fg=Theme.PRIMARY, bg=Theme.BG_WHITE,
                                bd=0, padx=0, cursor="hand2",
                                command=self.on_back)
            back_btn.pack(side="left")
        
        # Title
        title = f"New {self.doctype}" if self.is_new else f"{self.doctype}: {self.doc_name}"
        tk.Label(left_frame, text=title,
                 font=(Theme.FONT_FAMILY, 18, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(side="left", padx=20)
        
        # Status badge
        self.status_frame = tk.Frame(left_frame, bg=Theme.BG_WHITE)
        self.status_frame.pack(side="left")
        
        self.status_label = tk.Label(self.status_frame, text="Draft",
                                     font=(Theme.FONT_FAMILY, 9, "bold"),
                                     fg=Theme.TEXT_LIGHT, bg=Theme.TEXT_MUTED,
                                     padx=10, pady=3)
        self.status_label.pack()
        
        # Right side - Action buttons
        btn_frame = tk.Frame(header, bg=Theme.BG_WHITE)
        btn_frame.pack(side="right")
        
        # Cancel button (Red) - for submitted docs
        self.cancel_btn = tk.Button(btn_frame, text="Cancel Document",
                                   font=(Theme.FONT_FAMILY, 10, "bold"),
                                   fg=Theme.TEXT_LIGHT, bg=Theme.DANGER,
                                   bd=0, padx=20, pady=10, cursor="hand2",
                                   command=self.cancel_doc)
        self.cancel_btn.pack(side="right", padx=5)
        
        # Submit button (Green)
        self.submit_btn = tk.Button(btn_frame, text="Submit",
                                   font=(Theme.FONT_FAMILY, 10, "bold"),
                                   fg=Theme.TEXT_LIGHT, bg=Theme.SUCCESS,
                                   bd=0, padx=20, pady=10, cursor="hand2",
                                   command=self.submit)
        self.submit_btn.pack(side="right", padx=5)
        
        # Save button (Primary Blue)
        self.save_btn = tk.Button(btn_frame, text="Save",
                                 font=(Theme.FONT_FAMILY, 10, "bold"),
                                 fg=Theme.TEXT_LIGHT, bg=Theme.PRIMARY,
                                 bd=0, padx=20, pady=10, cursor="hand2",
                                 command=self.save)
        self.save_btn.pack(side="right", padx=5)
        
        # Separator
        tk.Frame(self, bg=Theme.BORDER, height=1).pack(fill="x")
        
        # Scrollable form area
        form_container = tk.Frame(self, bg=Theme.BG_LIGHT)
        form_container.pack(fill="both", expand=True)
        
        # Canvas for scrolling
        canvas = tk.Canvas(form_container, bg=Theme.BG_LIGHT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        
        self.form_frame = tk.Frame(canvas, bg=Theme.BG_WHITE, padx=30, pady=25)
        
        self.form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw", width=canvas.winfo_width())
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas.find_withtag("all")[0], width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build form fields from metadata
        self.build_form()
        self.update_button_states()
    
    def build_form(self):
        """Build form fields from DocType metadata"""
        fields = self.meta.get("fields", [])
        
        # Main fields section
        main_section = tk.LabelFrame(self.form_frame, text="Details",
                                     font=(Theme.FONT_FAMILY, 12, "bold"),
                                     fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE,
                                     bd=1, relief="solid", padx=20, pady=15)
        main_section.pack(fill="x", pady=(0, 20))
        
        row = 0
        for field in fields:
            fieldtype = field.get("fieldtype")
            fieldname = field.get("fieldname")
            
            # Skip certain field types
            if fieldtype in ["Section Break", "Column Break", "HTML", "Button"]:
                continue
            
            if fieldtype == "Table":
                # Child table in separate section
                self.create_table_field(self.form_frame, field)
            else:
                # Regular field
                self.create_field(main_section, field, row)
                row += 1
    
    def create_field(self, parent, field, row):
        """Create a form field with proper styling"""
        fieldtype = field.get("fieldtype")
        fieldname = field.get("fieldname")
        label = field.get("label", fieldname)
        options = field.get("options", "")
        reqd = field.get("reqd", 0)
        
        # Field row
        field_frame = tk.Frame(parent, bg=Theme.BG_WHITE)
        field_frame.pack(fill="x", pady=8)
        
        # Label
        label_text = f"{label} *" if reqd else label
        tk.Label(field_frame, text=label_text,
                 font=(Theme.FONT_FAMILY, 10),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE,
                 width=20, anchor="e").pack(side="left", padx=(0, 15))
        
        # Input based on type
        var = tk.StringVar()
        
        if fieldtype == "Select":
            opts = options.split("\n") if options else []
            widget = ttk.Combobox(field_frame, textvariable=var, values=opts, width=40)
            widget.pack(side="left", fill="x", expand=True)
        elif fieldtype == "Link":
            # Smart Lookup Field
            data_source = LookupService.get_data_source(options)
            id_var = tk.StringVar()
            name_var = tk.StringVar()
            
            widget = SmartLookupField(field_frame, 
                                    data_source=data_source,
                                    id_var=id_var,
                                    name_var=name_var,
                                    placeholder=f"Select {options}...")
            widget.pack(side="left", fill="x", expand=True)
            
            # FormView expects generic widget behavior for .var accessing
            widget.var = id_var # Used by load/collect_data
            
            # Monkey-patch internal var reference since SmartLookupField wraps it
            # But wait, create_field sets self.controls[fieldname] = {..., "var": var}
            # So setting var = id_var below handles it.
            var = id_var

        elif fieldtype == "Text" or fieldtype == "Small Text":
            widget = tk.Text(field_frame, height=3, width=42,
                            font=(Theme.FONT_FAMILY, 10),
                            bd=1, relief="solid")
            widget.pack(side="left", fill="x", expand=True)
            widget.var = None
        elif fieldtype == "Check":
            var = tk.BooleanVar()
            widget = ttk.Checkbutton(field_frame, variable=var)
            widget.pack(side="left")
        elif fieldtype in ["Currency", "Float"]:
            widget = ttk.Entry(field_frame, textvariable=var, width=20)
            widget.pack(side="left")
        elif fieldtype == "Int":
            widget = ttk.Entry(field_frame, textvariable=var, width=15)
            widget.pack(side="left")
        elif fieldtype == "Date":
            widget = ttk.Entry(field_frame, textvariable=var, width=20)
            widget.pack(side="left")
            tk.Label(field_frame, text="(YYYY-MM-DD)",
                    font=(Theme.FONT_FAMILY, 9),
                    fg=Theme.TEXT_MUTED, bg=Theme.BG_WHITE).pack(side="left", padx=10)
        else:
            widget = ttk.Entry(field_frame, textvariable=var, width=42)
            widget.pack(side="left", fill="x", expand=True)
        
        self.controls[fieldname] = {"widget": widget, "var": var, "fieldtype": fieldtype}
    
    def create_table_field(self, parent, field):
        """Create a child table field"""
        fieldname = field.get("fieldname")
        label = field.get("label", fieldname)
        child_doctype = field.get("options")
        
        # Table section
        table_section = tk.LabelFrame(parent, text=label,
                                      font=(Theme.FONT_FAMILY, 12, "bold"),
                                      fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE,
                                      bd=1, relief="solid", padx=20, pady=15)
        table_section.pack(fill="both", expand=True, pady=10)
        
        # Get child meta
        child_meta = frappe.get_meta(child_doctype)
        child_fields = child_meta.get("fields", [])
        
        # Filter to displayable fields
        display_fields = [f for f in child_fields if f.get("fieldtype") in 
                         ["Data", "Link", "Int", "Float", "Currency", "Select"]][:6]
        
        columns = [f.get("fieldname") for f in display_fields]
        headers = [f.get("label", f.get("fieldname")) for f in display_fields]
        
        # Treeview for table
        tree_frame = tk.Frame(table_section, bg=Theme.BG_WHITE)
        tree_frame.pack(fill="both", expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=6)
        
        for col, header in zip(columns, headers):
            tree.heading(col, text=header)
            tree.column(col, width=120, minwidth=80)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scroll.set)
        
        tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Add/Remove buttons
        btn_frame = tk.Frame(table_section, bg=Theme.BG_WHITE)
        btn_frame.pack(fill="x", pady=(15, 0))
        
        add_btn = tk.Button(btn_frame, text="+ Add Row",
                           font=(Theme.FONT_FAMILY, 10),
                           fg=Theme.TEXT_LIGHT, bg=Theme.PRIMARY,
                           bd=0, padx=15, pady=6, cursor="hand2",
                           command=lambda: self.add_table_row(fieldname, tree, display_fields))
        add_btn.pack(side="left", padx=(0, 10))
        
        remove_btn = tk.Button(btn_frame, text="- Remove Row",
                              font=(Theme.FONT_FAMILY, 10),
                              fg=Theme.DANGER, bg=Theme.BG_WHITE,
                              bd=1, padx=15, pady=5, cursor="hand2",
                              command=lambda: self.remove_table_row(tree))
        remove_btn.pack(side="left")
        
        self.child_tables[fieldname] = {
            "tree": tree,
            "fields": display_fields,
            "doctype": child_doctype
        }
    
    def add_table_row(self, fieldname, tree, fields):
        """Add a row to child table - CONNECTED TO BACKEND"""
        dialog = tk.Toplevel(self)
        dialog.title("Add Row")
        dialog.geometry("450x400")
        dialog.configure(bg=Theme.BG_WHITE)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (225)
        y = (dialog.winfo_screenheight() // 2) - (200)
        dialog.geometry(f"+{x}+{y}")
        
        # Header
        tk.Label(dialog, text="Add New Row",
                 font=(Theme.FONT_FAMILY, 14, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(pady=20)
        
        entries = {}
        form_frame = tk.Frame(dialog, bg=Theme.BG_WHITE)
        form_frame.pack(fill="both", expand=True, padx=30)
        
        for i, field in enumerate(fields):
            fname = field.get("fieldname")
            label = field.get("label", fname)
            
            row_frame = tk.Frame(form_frame, bg=Theme.BG_WHITE)
            row_frame.pack(fill="x", pady=8)
            
            tk.Label(row_frame, text=label,
                    font=(Theme.FONT_FAMILY, 10),
                    fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE,
                    width=15, anchor="e").pack(side="left", padx=(0, 10))
            
            var = tk.StringVar()
            
            if field.get("fieldtype") == "Link":
                # Use Smart Lookup for Link fields in child table
                doctype = field.get("options")
                ds = LookupService.get_data_source(doctype)
                name_var = tk.StringVar()
                
                # Auto-fill price
                def on_select(id, name, extra):
                    if extra:
                        # Try standard price fields
                        price = extra.get('selling_price') or extra.get('standard_rate')
                        if price:
                            for pf in ['rate', 'price', 'unit_price', 'amount']:
                                if pf in entries:
                                    entries[pf].set(str(price))
                                    break
                
                lookup = SmartLookupField(row_frame,
                                        data_source=ds,
                                        id_var=var,
                                        name_var=name_var,
                                        on_select=on_select,
                                        placeholder=f"Search {doctype}...",
                                        width=200)
                lookup.pack(side="left", fill="x", expand=True)
            else:
                entry = ttk.Entry(row_frame, textvariable=var, width=25)
                entry.pack(side="left", fill="x", expand=True)
                
            entries[fname] = var

        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=Theme.BG_WHITE)
        btn_frame.pack(pady=20)
        
        def save_row(close=True):
            values = [entries[f.get("fieldname")].get() for f in fields]
            tree.insert("", "end", values=values)
            if close:
                dialog.destroy()
            else:
                # Clear fields but keep focus
                for fname, var in entries.items():
                    var.set("")
                # Reset focus to first field (SmartLookup or Entry)
                # Ideally find the first widget. For now, just clearing is good help.
        
        def auto_calc(*args):
            try:
                # specific logic for standard fields
                qty = 0
                rate = 0
                if 'qty' in entries and entries['qty'].get():
                    qty = float(entries['qty'].get())
                if 'rate' in entries and entries['rate'].get():
                    rate = float(entries['rate'].get())
                
                if 'amount' in entries:
                     entries['amount'].set(f"{qty * rate:.2f}")
            except:
                pass
                
        # Bind triggers
        if 'qty' in entries: entries['qty'].trace_add('write', auto_calc)
        if 'rate' in entries: entries['rate'].trace_add('write', auto_calc)
        
        tk.Button(btn_frame, text="Cancel",
                 font=(Theme.FONT_FAMILY, 10),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE,
                 bd=1, padx=15, pady=8, cursor="hand2",
                 command=dialog.destroy).pack(side="left", padx=5)
                 
        tk.Button(btn_frame, text="Add & New",
                 font=(Theme.FONT_FAMILY, 10, "bold"),
                 fg=Theme.PRIMARY, bg=Theme.BG_WHITE,
                 bd=1, padx=15, pady=8, cursor="hand2",
                 command=lambda: save_row(close=False)).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Add",
                 font=(Theme.FONT_FAMILY, 10, "bold"),
                 fg=Theme.TEXT_LIGHT, bg=Theme.PRIMARY,
                 bd=0, padx=20, pady=8, cursor="hand2",
                 command=lambda: save_row(close=True)).pack(side="left", padx=5)
    
    def remove_table_row(self, tree):
        """Remove selected row from child table"""
        selected = tree.selection()
        if selected:
            tree.delete(selected[0])
        else:
            messagebox.showwarning("Warning", "Please select a row to remove")
    
    def load_data(self):
        """Load document data into form - FROM BACKEND"""
        # Update status badge
        docstatus = self.doc._data.get('docstatus', 0)
        status = self.doc._data.get('status', 'Draft')
        
        if docstatus == 0:
            self.status_label.config(text="Draft", bg=Theme.TEXT_MUTED)
        elif docstatus == 1:
            self.status_label.config(text="Submitted", bg=Theme.SUCCESS)
        elif docstatus == 2:
            self.status_label.config(text="Cancelled", bg=Theme.DANGER)
        
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
            self.save_btn.config(state="normal", bg=Theme.PRIMARY)
            self.submit_btn.config(state="normal", bg=Theme.SUCCESS)
            self.cancel_btn.pack_forget()
        elif docstatus == 1:  # Submitted
            self.save_btn.pack_forget()
            self.submit_btn.pack_forget()
            self.cancel_btn.pack(side="right", padx=5)
            self.cancel_btn.config(state="normal", bg=Theme.DANGER)
        else:  # Cancelled
            self.save_btn.pack_forget()
            self.submit_btn.pack_forget()
            self.cancel_btn.pack_forget()
    
    def collect_data(self):
        """Collect form data into document - FOR BACKEND"""
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
        """Save the document - CALLS BACKEND CONTROLLER"""
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
        """Submit the document - CALLS BACKEND CONTROLLER on_submit()"""
        try:
            if self.is_new:
                self.collect_data()
                self.doc.save()
            else:
                self.collect_data()
            
            # Call controller's submit method
            self.doc.submit()
            messagebox.showinfo("Success", f"Submitted {self.doctype}: {self.doc.name}\n\nStock has been reserved.")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def cancel_doc(self):
        """Cancel the document - CALLS BACKEND CONTROLLER on_cancel()"""
        try:
            if messagebox.askyesno("Confirm Cancel", 
                                   f"Cancel {self.doctype}: {self.doc.name}?\n\nThis will unreserve stock."):
                # Call controller's cancel method
                self.doc.cancel()
                messagebox.showinfo("Success", f"Cancelled {self.doctype}: {self.doc.name}")
                self.load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))
