
import tkinter as tk
from tkinter import ttk, messagebox
from ui.widgets.smart_lookup import SmartLookupField
from modules.lookup_service import LookupService
from ui.framework.desk_styles import Theme
from core.database import get_db
from datetime import datetime

class NewPurchaseOrderDialog(tk.Toplevel):
    """
    Dialog to create a new Purchase Order.
    Uses SmartLookupField for Supplier and Product selection.
    """
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.title("New Purchase Order")
        self.geometry("900x650")
        self.configure(bg=Theme.BG_WHITE)
        self.transient(parent)
        self.grab_set()
        
        self.items = [] # List of dicts: product_id, product_name, qty, cost, total
        
        self.setup_ui()
        
        # Center the dialog
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')

    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg=Theme.BG_WHITE)
        header.pack(fill='x', padx=20, pady=15)
        
        tk.Label(header, text="New Purchase Order", font=("Segoe UI", 18, "bold"), 
                 bg=Theme.BG_WHITE, fg=Theme.PRIMARY).pack(side='left')
        
        # Main Content Area (Two Columns)
        content = tk.Frame(self, bg=Theme.BG_WHITE)
        content.pack(fill='both', expand=True, padx=20)
        
        left_panel = tk.Frame(content, bg=Theme.BG_WHITE, width=350)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)
        
        right_panel = tk.Frame(content, bg=Theme.BG_WHITE)
        right_panel.pack(side='left', fill='both', expand=True)

        # --- LEFT PANEL: Supplier & Item Entry ---
        
        # Supplier Lookup
        self.supp_id_var = tk.StringVar()
        self.supp_name_var = tk.StringVar()
        
        self.supp_lookup = SmartLookupField(
            left_panel,
            label="Supplier",
            data_source=LookupService.get_suppliers,
            id_var=self.supp_id_var,
            name_var=self.supp_name_var,
            placeholder="Search Supplier...",
            required=True
        )
        self.supp_lookup.pack(fill='x', pady=(0, 20))
        
        ttk.Separator(left_panel, orient='horizontal').pack(fill='x', pady=10)
        
        tk.Label(left_panel, text="Add Item", font=("Segoe UI", 11, "bold"), 
                 bg=Theme.BG_WHITE, fg=Theme.TEXT_MUTED).pack(anchor='w', pady=(0, 10))

        # Product Lookup
        self.prod_id_var = tk.StringVar()
        self.prod_name_var = tk.StringVar()
        
        self.prod_lookup = SmartLookupField(
            left_panel,
            label="Product",
            data_source=LookupService.get_products,
            id_var=self.prod_id_var,
            name_var=self.prod_name_var,
            placeholder="Search Product...",
            on_select=self._on_product_selected
        )
        self.prod_lookup.pack(fill='x', pady=(0, 10))
        
        # Row for Qty and Cost
        row_qc = tk.Frame(left_panel, bg=Theme.BG_WHITE)
        row_qc.pack(fill='x', pady=(0, 10))
        
        # Quantity
        f_qty = tk.Frame(row_qc, bg=Theme.BG_WHITE)
        f_qty.pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Label(f_qty, text="Qty", font=("Segoe UI", 9), bg=Theme.BG_WHITE).pack(anchor='w')
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(f_qty, textvariable=self.qty_var).pack(fill='x')
        
        # Cost Price
        f_cost = tk.Frame(row_qc, bg=Theme.BG_WHITE)
        f_cost.pack(side='left', fill='x', expand=True, padx=(5, 0))
        tk.Label(f_cost, text="Unit Cost", font=("Segoe UI", 9), bg=Theme.BG_WHITE).pack(anchor='w')
        self.cost_var = tk.StringVar()
        ttk.Entry(f_cost, textvariable=self.cost_var).pack(fill='x')
        
        # Add Button
        ttk.Button(left_panel, text="Add Item ⬇", command=self.add_item).pack(fill='x', pady=10)
        
        # --- RIGHT PANEL: Items List ---
        
        # Treeview
        cols = ('code', 'name', 'qty', 'cost', 'total')
        self.tree = ttk.Treeview(right_panel, columns=cols, show='headings', height=15)
        
        self.tree.heading('code', text='Code')
        self.tree.heading('name', text='Product')
        self.tree.heading('qty', text='Qty')
        self.tree.heading('cost', text='Cost')
        self.tree.heading('total', text='Total')
        
        self.tree.column('code', width=80)
        self.tree.column('name', width=200)
        self.tree.column('qty', width=60, anchor='center')
        self.tree.column('cost', width=80, anchor='e')
        self.tree.column('total', width=80, anchor='e')
        
        self.tree.pack(fill='both', expand=True, pady=(0, 10))
        
        # Totals
        total_frame = tk.Frame(right_panel, bg=Theme.BG_WHITE)
        total_frame.pack(fill='x', pady=10)
        
        self.total_lbl = tk.Label(total_frame, text="Total: $0.00", font=("Segoe UI", 16, "bold"), 
                                  bg=Theme.BG_WHITE, fg=Theme.PRIMARY)
        self.total_lbl.pack(side='right')

        # Footer Actions
        footer = tk.Frame(self, bg=Theme.BG_WHITE)
        footer.pack(fill='x', side='bottom', padx=20, pady=20)
        
        ttk.Button(footer, text="Cancel", command=self.destroy).pack(side='right', padx=5)
        ttk.Button(footer, text="Create Order", style='Success.TButton', command=self.save_order).pack(side='right')

    def _on_product_selected(self, prod_id, name, extra):
        # Auto-fill cost price if available (using 'cost_price' from extra data)
        if extra and 'cost_price' in extra:
            self.cost_var.set(str(extra['cost_price']))
        else:
            self.cost_var.set("0.0")
            
    def add_item(self):
        prod_id = self.prod_id_var.get()
        if not prod_id:
            messagebox.showwarning("Input Error", "Please select a product.")
            return
            
        try:
            qty = int(self.qty_var.get())
            cost = float(self.cost_var.get())
            if qty <= 0 or cost < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid quantity or cost.")
            return
            
        total = qty * cost
        
        # Add to list
        item = {
            'product_id': prod_id,
            'product_name': self.prod_name_var.get(),
            'quantity': qty,
            'cost_price': cost,
            'total': total
        }
        self.items.append(item)
        
        # Update Tree
        self.tree.insert('', 'end', values=(
            prod_id, 
            item['product_name'], 
            qty, 
            f"${cost:.2f}", 
            f"${total:.2f}"
        ))
        
        # Update Totals
        self._update_total()
        
        # Reset Item Inputs
        self.prod_lookup.clear()
        self.qty_var.set("1")
        self.cost_var.set("")
        
        # Focus back on product lookup for rapid entry
        self.prod_lookup.entry.focus()

    def _update_total(self):
        grand_total = sum(i['total'] for i in self.items)
        self.total_lbl.config(text=f"Total: ${grand_total:,.2f}")

    def save_order(self):
        supplier_id = self.supp_id_var.get()
        if not supplier_id:
            messagebox.showwarning("Missing Data", "Please select a supplier.")
            return
            
        if not self.items:
            messagebox.showwarning("Missing Data", "Please add at least one item.")
            return
            
        # Save to DB logic here
        # For now, pseudo-code as PurchaseService might not be fully ready
        try:
            db = get_db()
            # Generate PO Number
            po_num = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            with db.transaction():
                # Create PO Header
                total = sum(i['total'] for i in self.items)
                db.insert('purchase_orders', {
                    'po_number': po_num,
                    'supplier_id': supplier_id,
                    'order_date': datetime.now().strftime('%Y-%m-%d'),
                    'total_amount': total,
                    'status': 'Draft',
                    'created_by': self.user_data.get('id', 0)
                })
                
                # Create PO Items
                for item in self.items:
                    db.insert('purchase_order_items', {
                        'po_number': po_num,
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'unit_price': item['cost_price'],
                        'total_price': item['total']
                    })
            
            messagebox.showinfo("Success", f"Purchase Order {po_num} created!")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create order: {str(e)}")


class NewSupplierDialog(tk.Toplevel):
    """
    Dialog to create a new Supplier.
    Basic form, no lookups needed inside, but creates an entity for lookup.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Supplier")
        self.geometry("400x350")
        self.configure(bg=Theme.BG_WHITE)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'+{x}+{y}')

    def setup_ui(self):
        frame = tk.Frame(self, bg=Theme.BG_WHITE, padx=20, pady=20)
        frame.pack(fill='both', expand=True)
        
        tk.Label(frame, text="New Supplier", font=("Segoe UI", 16, "bold"), 
                 bg=Theme.BG_WHITE, fg=Theme.PRIMARY).pack(anchor='w', pady=(0, 20))
        
        # Name
        tk.Label(frame, text="Supplier Name *", bg=Theme.BG_WHITE).pack(anchor='w')
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var).pack(fill='x', pady=(0, 10))
        
        # Contact
        tk.Label(frame, text="Contact Person", bg=Theme.BG_WHITE).pack(anchor='w')
        self.contact_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.contact_var).pack(fill='x', pady=(0, 10))
        
        # Email
        tk.Label(frame, text="Email", bg=Theme.BG_WHITE).pack(anchor='w')
        self.email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_var).pack(fill='x', pady=(0, 20))
        
        # Save Button
        ttk.Button(frame, text="Creating Supplier", style='Success.TButton', command=self.save).pack(fill='x')

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
            
        try:
            db = get_db()
            # Generate ID
            cust_id = name[:3].upper() + datetime.now().strftime('%M%S')
            
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.insert('tabSupplier', {
                'name': cust_id,
                'supplier_name': name,
                'supplier_type': 'Individual',
                'docstatus': 0,
                'owner': 'Administrator',
                'creation': now_str,
                'modified': now_str
            })
            
            # Invalidate cache
            try:
                LookupService.invalidate_suppliers()
            except:
                pass
                
            messagebox.showinfo("Success", f"Supplier {name} created!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
