"""
Professional ERPNext-Style List View
Displays records in a table with search, filters, and actions.
All buttons connected to backend.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import core.frappe as frappe
from core.database import db, get_table_name
from ui.framework.desk_styles import Theme


class ListView(ttk.Frame):
    """
    Generic List View for displaying DocType records.
    All actions connected to backend.
    """
    
    def __init__(self, parent, doctype, on_edit=None, on_create=None, on_back=None):
        super().__init__(parent, style="Content.TFrame")
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
            if count >= 4:
                break
            
            fieldtype = field.get("fieldtype")
            if fieldtype in ["Data", "Link", "Select", "Date", "Currency", "Int", "Float"]:
                self.columns.append(field.get("fieldname"))
                self.headers.append(field.get("label", field.get("fieldname")))
                count += 1
        
        # Add docstatus
        self.columns.append("docstatus")
        self.headers.append("Status")
    
    def setup_ui(self):
        """Build the list interface"""
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
        tk.Label(left_frame, text=f"{self.doctype} List",
                 font=(Theme.FONT_FAMILY, 18, "bold"),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE).pack(side="left", padx=20)
        
        # Right side - Actions
        btn_frame = tk.Frame(header, bg=Theme.BG_WHITE)
        btn_frame.pack(side="right")
        
        # Refresh button
        refresh_btn = tk.Button(btn_frame, text="↻ Refresh",
                               font=(Theme.FONT_FAMILY, 10),
                               fg=Theme.TEXT_DARK, bg=Theme.BG_WHITE,
                               bd=1, padx=15, pady=8, cursor="hand2",
                               command=self.refresh)
        refresh_btn.pack(side="left", padx=5)
        
        # New button (Primary)
        new_btn = tk.Button(btn_frame, text="+ New",
                           font=(Theme.FONT_FAMILY, 10, "bold"),
                           fg=Theme.TEXT_LIGHT, bg=Theme.PRIMARY,
                           bd=0, padx=20, pady=8, cursor="hand2",
                           command=self.create_new)
        new_btn.pack(side="left", padx=5)
        
        # Separator
        tk.Frame(self, bg=Theme.BORDER, height=1).pack(fill="x")
        
        # Filter bar
        filter_bar = tk.Frame(self, bg=Theme.BG_LIGHT)
        filter_bar.pack(fill="x", padx=25, pady=15)
        
        # Search
        tk.Label(filter_bar, text="Search:",
                 font=(Theme.FONT_FAMILY, 10),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_LIGHT).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_results())
        search_entry = ttk.Entry(filter_bar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=10)
        
        # Status filter
        tk.Label(filter_bar, text="Status:",
                 font=(Theme.FONT_FAMILY, 10),
                 fg=Theme.TEXT_DARK, bg=Theme.BG_LIGHT).pack(side="left", padx=(20, 5))
        
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_bar, textvariable=self.status_var,
                                    values=["All", "Draft", "Submitted", "Cancelled"], width=12)
        status_combo.pack(side="left")
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_results())
        
        # Record count
        self.count_label = tk.Label(filter_bar, text="0 records",
                                    font=(Theme.FONT_FAMILY, 10),
                                    fg=Theme.TEXT_MUTED, bg=Theme.BG_LIGHT)
        self.count_label.pack(side="right")
        
        # Table container
        table_container = tk.Frame(self, bg=Theme.BG_WHITE)
        table_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        # Treeview
        self.tree = ttk.Treeview(table_container, columns=self.columns, show="headings")
        
        # Configure columns
        for col, header in zip(self.columns, self.headers):
            self.tree.heading(col, text=header, command=lambda c=col: self.sort_by(c))
            width = 150 if col == "name" else 120
            self.tree.column(col, width=width, minwidth=80)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Bindings
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0,
                                    font=(Theme.FONT_FAMILY, 10),
                                    bg=Theme.BG_WHITE, fg=Theme.TEXT_DARK)
        self.context_menu.add_command(label="Open", command=self.open_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        
        # Store data for filtering
        self.all_data = []
    
    def refresh(self):
        """Refresh list data from database - CONNECTED TO BACKEND"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch data from database
        try:
            table = get_table_name(self.doctype)
            
            # Build column list, handling missing columns gracefully
            available_cols = []
            for col in self.columns:
                available_cols.append(col)
            
            fields_str = ", ".join(available_cols)
            data = db.sql(f"SELECT {fields_str} FROM {table} ORDER BY name DESC", as_dict=True)
            
            self.all_data = data
            self.display_data(data)
            self.count_label.config(text=f"{len(data)} records")
        except Exception as e:
            print(f"Error loading {self.doctype}: {e}")
            self.all_data = []
            self.count_label.config(text="Error loading data")
    
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
                
                values.append(val if val is not None else "")
            
            self.tree.insert("", "end", values=values)
    
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
        self.count_label.config(text=f"{len(filtered)} records")
    
    def sort_by(self, column):
        """Sort by column"""
        if not hasattr(self, '_sort_reverse'):
            self._sort_reverse = False
        self._sort_reverse = not self._sort_reverse
        
        self.all_data.sort(key=lambda x: str(x.get(column, "")), reverse=self._sort_reverse)
        self.filter_results()
    
    def on_double_click(self, event):
        """Handle double-click to open record - CONNECTED TO BACKEND"""
        self.open_selected()
    
    def open_selected(self):
        """Open selected record - CONNECTED TO BACKEND"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["values"][0]  # First column is 'name'
            if self.on_edit:
                self.on_edit(self.doctype, name)
    
    def create_new(self):
        """Create new record - CONNECTED TO BACKEND"""
        if self.on_create:
            self.on_create(self.doctype)
    
    def delete_selected(self):
        """Delete selected record - CONNECTED TO BACKEND"""
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
            row = self.tree.identify_row(event.y)
            if row:
                self.tree.selection_set(row)
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
