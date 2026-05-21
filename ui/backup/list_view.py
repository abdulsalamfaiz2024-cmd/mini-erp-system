"""
Professional ERPNext-Style List View
Displays records in a table with search, filters, and actions.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import core.frappe as frappe
from core.database import db, get_table_name


class ListView(ttk.Frame):
    """
    Generic List View for displaying DocType records.
    Features: Search, Filters, New/Edit/Delete actions.
    """
    
    def __init__(self, parent, doctype, on_edit=None, on_create=None, on_back=None):
        super().__init__(parent)
        self.doctype = doctype
        self.on_edit = on_edit
        self.on_create = on_create
        self.on_back = on_back
        
        self.meta = frappe.get_meta(doctype)
        self.setup_columns()
        self.setup_ui()
        self.refresh()
    
    def setup_columns(self):
        """Determine which columns to show"""
        fields = self.meta.get("fields", [])
        
        # Start with 'name' column
        self.columns = ["name"]
        self.headers = ["ID"]
        
        # Add first few data fields
        count = 0
        for field in fields:
            if count >= 5:
                break
            
            fieldtype = field.get("fieldtype")
            if fieldtype in ["Data", "Link", "Select", "Date", "Currency", "Int", "Float"]:
                self.columns.append(field.get("fieldname"))
                self.headers.append(field.get("label", field.get("fieldname")))
                count += 1
        
        # Add status if exists
        if "status" not in self.columns:
            self.columns.append("docstatus")
            self.headers.append("Status")
    
    def setup_ui(self):
        """Build the list interface"""
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=15)
        
        # Back button
        if self.on_back:
            ttk.Button(header, text="< Back", command=self.on_back).pack(side="left")
        
        # Title
        ttk.Label(header, text=f"{self.doctype} List", 
                  font=("Segoe UI", 16, "bold")).pack(side="left", padx=20)
        
        # Action buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, text="+ New", command=self.create_new).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side="left", padx=5)
        
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_results())
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=10)
        
        # Filter by status
        ttk.Label(search_frame, text="Status:").pack(side="left", padx=10)
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_var, 
                                     values=["All", "Draft", "Submitted", "Cancelled"], width=15)
        status_combo.pack(side="left")
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_results())
        
        # Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical")
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings",
                                  yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)
        
        # Configure columns
        for col, header in zip(self.columns, self.headers):
            self.tree.heading(col, text=header, command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=120, minwidth=80)
        
        # Pack
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        
        # Bind double-click to edit
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Store all data for filtering
        self.all_data = []
    
    def refresh(self):
        """Refresh list data from database"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch data
        try:
            table = get_table_name(self.doctype)
            fields_str = ", ".join(self.columns)
            data = db.sql(f"SELECT {fields_str} FROM {table} ORDER BY name DESC", as_dict=True)
            
            self.all_data = data
            self.display_data(data)
        except Exception as e:
            print(f"Error loading {self.doctype}: {e}")
            self.all_data = []
    
    def display_data(self, data):
        """Display data in treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for row in data:
            values = []
            for col in self.columns:
                val = row.get(col, "")
                
                # Format docstatus
                if col == "docstatus":
                    if val == 0:
                        val = "Draft"
                    elif val == 1:
                        val = "Submitted"
                    elif val == 2:
                        val = "Cancelled"
                
                values.append(val)
            
            self.tree.insert("", "end", values=values, tags=('row',))
    
    def filter_results(self):
        """Filter displayed results"""
        search = self.search_var.get().lower()
        status = self.status_var.get()
        
        filtered = []
        for row in self.all_data:
            # Status filter
            docstatus = row.get('docstatus', 0)
            if status != "All":
                if status == "Draft" and docstatus != 0:
                    continue
                elif status == "Submitted" and docstatus != 1:
                    continue
                elif status == "Cancelled" and docstatus != 2:
                    continue
            
            # Search filter
            if search:
                matched = False
                for col in self.columns:
                    val = str(row.get(col, "")).lower()
                    if search in val:
                        matched = True
                        break
                if not matched:
                    continue
            
            filtered.append(row)
        
        self.display_data(filtered)
    
    def sort_by(self, column):
        """Sort by column"""
        # Toggle sort direction
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = False
        self._sort_reverse = not self._sort_reverse
        
        self.all_data.sort(key=lambda x: str(x.get(column, "")), reverse=self._sort_reverse)
        self.filter_results()
    
    def on_double_click(self, event):
        """Handle double-click to open record"""
        self.open_selected()
    
    def open_selected(self):
        """Open selected record"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["values"][0]  # First column is 'name'
            if self.on_edit:
                self.on_edit(self.doctype, name)
    
    def create_new(self):
        """Create new record"""
        if self.on_create:
            self.on_create(self.doctype)
    
    def delete_selected(self):
        """Delete selected record"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["values"][0]
            
            if messagebox.askyesno("Confirm Delete", f"Delete {self.doctype}: {name}?"):
                try:
                    table = get_table_name(self.doctype)
                    db.sql(f"DELETE FROM {table} WHERE name = ?", (name,))
                    db.commit()
                    self.refresh()
                    messagebox.showinfo("Success", f"Deleted {name}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        try:
            self.tree.selection_set(self.tree.identify_row(event.y))
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
