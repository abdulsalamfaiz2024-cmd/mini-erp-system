"""
Sales Dialogs
Dialog components for sales order management

Enhanced with SmartLookupField for:
- Autocomplete suggestions when typing
- Dropdown button for full selection list
- Bi-directional ID/Name binding
- Auto price-fill on product selection
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ui.styles import Theme
from ui.modern_widgets import ModernTable, ModernForm
from ui.widgets.smart_lookup import SmartLookupField
from ui.workflow_widgets import WorkflowStatusLabel
from modules.sales.sales_manager import SalesManager
from modules.sales.service import SalesOrderService
from modules.workflow.service import WorkflowService
from modules.reporting.invoice_generator import InvoiceGenerator
from modules.lookup_service import LookupService
from core.database import get_db
import os
from datetime import datetime



class NewOrderDialog(tk.Toplevel):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.title("New Sales Invoice")
        self.geometry("1000x600")
        Theme.apply_styles(self)
        
        # Make Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        self.user_data = user_data
        self.items = []
        
        self.content = ttk.Frame(self, style='Main.TFrame', padding=20)
        self.content.pack(fill='both', expand=True)
        
        self.content.pack(fill='both', expand=True)
        
        # Determine Salesperson
        self.employee_id = None
        self.employee_name = "Unknown"
        try:
             db = get_db()
             row = db.fetch_one("SELECT employee_id, full_name FROM employees WHERE user_id = ?", (user_data['id'],))
             if row:
                 self.employee_id = row['employee_id']
                 self.employee_name = row['full_name']
        except:
             pass
             
        self.setup_content()
        
    def setup_content(self):
        # MAIN LAYOUT:
        # Top: Header (Salesperson)
        # Middle: Scrollable Area (Form + Table)
        # Bottom: Footer (Save Button)

        # 1. Header (Fixed)
        top = tk.Frame(self, bg=Theme.BG_WHITE)
        top.pack(fill='x', side='top', pady=(0, 10))
        ttk.Label(top, text=f"Salesperson: {self.employee_name}", style='Header.TLabel', background=Theme.BG_WHITE).pack(side='right', padx=20, pady=10)

        # 3. Footer (Fixed at Bottom)
        footer = tk.Frame(self, bg=Theme.BG_WHITE)
        footer.pack(fill='x', side='bottom', pady=10, padx=20)
        
        # Actions
        ttk.Button(footer, text="🚀 Publish to Finance", style='Success.TButton', command=self.submit_to_finance).pack(side='right', padx=5)
        ttk.Button(footer, text="💾 Save Draft", style='Primary.TButton', command=self.save_draft).pack(side='right', padx=5)

        # 2. Scrollable Middle
        # Container for Canvas + Scrollbar
        middle = tk.Frame(self, bg=Theme.BG_WHITE)
        middle.pack(fill='both', expand=True, side='top')
        
        canvas = tk.Canvas(middle, bg=Theme.BG_WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(middle, orient="vertical", command=canvas.yview)
        
        # Frame INSIDE canvas
        self.content = tk.Frame(canvas, bg=Theme.BG_WHITE)
        
        # Determine Window size for scroll region
        self.content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack Scroll components
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # --- Form Content (Inside self.content) ---
        
        # Two columns layout
        container = tk.Frame(self.content, bg=Theme.BG_WHITE)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        left = tk.Frame(container, bg=Theme.BG_WHITE)
        left.pack(side='left', fill='y', padx=(0, 20))
        left.configure(width=320)
        left.pack_propagate(False) 
        
        right = tk.Frame(container, bg=Theme.BG_WHITE)
        right.pack(side='left', fill='both', expand=True)
        
        # --- LEFT PANEL ---
        
        # Customer Selection with Smart Lookup
        # Features: Autocomplete, dropdown, bi-directional binding
        self.cust_id_var = tk.StringVar()
        self.cust_name_var = tk.StringVar()
        
        self.customer_lookup = SmartLookupField(
            left,
            label="Customer",
            data_source=LookupService.get_customers,
            id_var=self.cust_id_var,
            name_var=self.cust_name_var,
            on_select=self._on_customer_selected,
            placeholder="Search customer by name or ID...",
            required=True
        )
        self.customer_lookup.pack(fill='x', pady=(0, 20))
        
        # Product Selection Area
        ttk.Separator(left, orient='horizontal').pack(fill='x', pady=10)
        ttk.Label(left, text="Line Item Details", style='CardSub.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Product Selection with Smart Lookup & auto price-fill
        self.prod_id_var = tk.StringVar()
        self.prod_name_var = tk.StringVar()
        self._selected_product_data = {}  # Store extra data for add_item
        
        self.product_lookup = SmartLookupField(
            left,
            label="Product",
            data_source=LookupService.get_products,
            id_var=self.prod_id_var,
            name_var=self.prod_name_var,
            on_select=self._on_product_selected,
            placeholder="Search product by name or ID..."
        )
        self.product_lookup.pack(fill='x', pady=5)
        
        # Price (Editable) - auto-filled when product is selected
        self.price_var = tk.StringVar()
        
        self.qty_var = tk.StringVar(value="1")
        
        row1 = tk.Frame(left, bg=Theme.BG_WHITE)
        row1.pack(fill='x', pady=5)
        
        f_qty = tk.Frame(row1, bg=Theme.BG_WHITE)
        f_qty.pack(side='left', fill='x', expand=True, padx=(0,5))
        ttk.Label(f_qty, text="Qty", style='FormLabel.TLabel').pack(anchor='w')
        ttk.Entry(f_qty, textvariable=self.qty_var).pack(fill='x')
        
        f_price = tk.Frame(row1, bg=Theme.BG_WHITE)
        f_price.pack(side='left', fill='x', expand=True, padx=(5,0))
        ttk.Label(f_price, text="Price", style='FormLabel.TLabel').pack(anchor='w')
        ttk.Entry(f_price, textvariable=self.price_var).pack(fill='x')

        # Tax & Discount
        row2 = tk.Frame(left, bg=Theme.BG_WHITE)
        row2.pack(fill='x', pady=5)
        
        self.tax_var = tk.StringVar(value="0")
        f_tax = tk.Frame(row2, bg=Theme.BG_WHITE)
        f_tax.pack(side='left', fill='x', expand=True, padx=(0,5))
        ttk.Label(f_tax, text="Tax %", style='FormLabel.TLabel').pack(anchor='w')
        ttk.Entry(f_tax, textvariable=self.tax_var).pack(fill='x')
        
        self.disc_var = tk.StringVar(value="0")
        f_disc = tk.Frame(row2, bg=Theme.BG_WHITE)
        f_disc.pack(side='left', fill='x', expand=True, padx=(5,0))
        ttk.Label(f_disc, text="Disc ($)", style='FormLabel.TLabel').pack(anchor='w')
        ttk.Entry(f_disc, textvariable=self.disc_var).pack(fill='x')
        
        ttk.Button(left, text="Add Line", command=self.add_item).pack(fill='x', pady=20)
        
        # --- RIGHT PANEL ---
        cols = [
             {'name': 'name', 'text': 'Item', 'width': 180},
             {'name': 'qty', 'text': 'Qty', 'width': 50},
             {'name': 'price', 'text': 'Price', 'width': 70, 'anchor':'e'},
             {'name': 'tax', 'text': 'Tax', 'width': 60, 'anchor':'e'},
             {'name': 'disc', 'text': 'Disc', 'width': 60, 'anchor':'e'},
             {'name': 'total', 'text': 'Total', 'width': 80, 'anchor':'e'},
         ]
        self.table = ModernTable(right, cols)
        self.table.pack(fill='both', expand=True, pady=(0, 20))
        
        # Totals
        self.f_totals = tk.Frame(right, bg=Theme.BG_WHITE)
        self.f_totals.pack(anchor='e')
        
        self.lbl_sub = ttk.Label(self.f_totals, text="Subtotal: $0.00", style='CardSub.TLabel', background=Theme.BG_WHITE)
        self.lbl_sub.pack(anchor='e')
        self.lbl_tax = ttk.Label(self.f_totals, text="Tax: $0.00", style='CardSub.TLabel', background=Theme.BG_WHITE)
        self.lbl_tax.pack(anchor='e')
        self.lbl_disc = ttk.Label(self.f_totals, text="Discount: $0.00", style='CardSub.TLabel', background=Theme.BG_WHITE)
        self.lbl_disc.pack(anchor='e')
        ttk.Separator(self.f_totals, orient='horizontal').pack(fill='x', pady=5)
        self.total_lbl = ttk.Label(self.f_totals, text="Total: $0.00", style='H2.TLabel', background=Theme.BG_WHITE)
        self.total_lbl.pack(anchor='e')
        
    def _on_customer_selected(self, cust_id, cust_name, extra_data):
        """Callback when customer is selected from lookup"""
        # Could show customer info, credit limit, etc.
        pass
    
    def _on_product_selected(self, prod_id, prod_name, extra_data):
        """Callback when product is selected - auto-fill price"""
        self._selected_product_data = extra_data
        selling_price = extra_data.get('selling_price', 0)
        if selling_price:
            self.price_var.set(str(selling_price))
    
    def add_item(self):
        """Add product line item to order"""
        prod_id = self.prod_id_var.get()
        prod_name = self.prod_name_var.get()
        
        if not prod_id or not prod_name:
            messagebox.showwarning("Missing Product", "Please select a product first.")
            return
            
        try:
            qty = int(self.qty_var.get())
            price = float(self.price_var.get())
            tax_rate = float(self.tax_var.get())
            disc = float(self.disc_var.get())
            if qty <= 0:
                messagebox.showwarning("Invalid Quantity", "Quantity must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantity, price, tax, and discount.")
            return
        
        # Calculate totals
        gross = qty * price
        taxable = gross - disc
        tax_amt = taxable * (tax_rate / 100.0)
        total = taxable + tax_amt
        
        self.items.append({
            'product_id': prod_id,
            'name': prod_name,
            'quantity': qty,
            'unit_price': price,
            'tax_rate': tax_rate,
            'tax_amount': tax_amt,
            'discount_amount': disc,
            'total_price': total,
            'gross': gross
        })
        
        # Clear product fields for next entry
        self.product_lookup.clear()
        self.price_var.set('')
        self.qty_var.set('1')
        self.tax_var.set('0')
        self.disc_var.set('0')
        
        self.refresh()
        
    def refresh(self):
        rows = []
        sub = 0
        tax = 0
        disc = 0
        grand = 0
        
        for i in self.items:
            rows.append((
                i['name'], 
                i['quantity'], 
                f"${i['unit_price']:.2f}", 
                f"{i['tax_rate']}% (${i['tax_amount']:.2f})",
                f"${i['discount_amount']:.2f}",
                f"${i['total_price']:.2f}"
            ))
            sub += i['gross']
            tax += i['tax_amount']
            disc += i['discount_amount']
            grand += i['total_price']
            
        self.table.set_data(rows)
        self.lbl_sub.configure(text=f"Subtotal: ${sub:,.2f}")
        self.lbl_tax.configure(text=f"Tax: ${tax:,.2f}")
        self.lbl_disc.configure(text=f"Discount: ${disc:,.2f}")
        self.total_lbl.configure(text=f"Total: ${grand:,.2f}")
        
    def save_draft(self):
        self._save(submit=False)
        
    def submit_to_finance(self):
        if messagebox.askyesno("Confirm", "Create and Publish this order to Finance?"):
            self._save(submit=True)

    def _save(self, submit=False):
        """Save the order (draft or submit to finance)"""
        cust_id = self.cust_id_var.get()
        cust_name = self.cust_name_var.get()
        
        if not cust_id:
            messagebox.showerror("Missing Customer", "Please select a customer.")
            return
            
        if not self.items:
            messagebox.showerror("No Items", "Please add at least one line item.")
            return
            
        try:
            uid = self.user_data['id']
            # Use customer ID from SmartLookupField
            order_id = SalesOrderService.create_order(cust_id, self.items, self.employee_id, uid)
            
            if submit:
                SalesOrderService.submit_order(order_id, self.employee_id)
                messagebox.showinfo("Success", f"Order {order_id} Published to Finance!")
            else:
                messagebox.showinfo("Success", f"Order {order_id} Saved as Draft.")
                
            self.master.load_data() 
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class ViewOrderDialog(tk.Toplevel):
    def __init__(self, parent, order_num, user_data):
        super().__init__(parent)
        self.title(f"Invoice {order_num}")
        self.geometry("900x600")
        Theme.apply_styles(self)
        
        # Make Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        self.order_num = order_num
        self.user_data = user_data
        
        self.content = ttk.Frame(self, style='Main.TFrame', padding=20)
        self.content.pack(fill='both', expand=True)
        
        # Simple info + Table
        self.info_frame = tk.Frame(self.content, bg=Theme.BG_WHITE)
        self.info_frame.pack(fill='x', pady=(0, 20))
        
        self.lbl_info = ttk.Label(self.info_frame, text="Loading...", background=Theme.BG_WHITE, font=("Segoe UI", 12))
        self.lbl_info.pack(anchor='w')
        self.lbl_status = ttk.Label(self.info_frame, text="", background=Theme.BG_WHITE, font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(anchor='w')
        
        cols = [
             {'name': 'name', 'text': 'Item', 'width': 200},
             {'name': 'qty', 'text': 'Qty', 'width': 60},
             {'name': 'price', 'text': 'Unit', 'width': 80, 'anchor':'e'},
             {'name': 'tax', 'text': 'Tax', 'width': 80, 'anchor':'e'},
             {'name': 'disc', 'text': 'Disc', 'width': 80, 'anchor':'e'},
             {'name': 'total', 'text': 'Total', 'width': 100, 'anchor':'e'},
        ]
        self.table = ModernTable(self.content, cols)
        self.table.pack(fill='both', expand=True)
        
        self.f_totals = tk.Frame(self.content, bg=Theme.BG_WHITE)
        self.f_totals.pack(anchor='e', pady=10)
        self.lbl_totals = ttk.Label(self.f_totals, text="", style='H2.TLabel', background=Theme.BG_WHITE, anchor='e', justify='right')
        self.lbl_totals.pack()
        
        self.load()
        
    def load(self):
        db = get_db()
        order = db.fetch_one("SELECT * FROM sales_orders WHERE order_number=?", (self.order_num,))
        if not order: return
        
        # Get Workflow State
        wf = getattr(WorkflowService.get_current_state('SALES_ORDER', self.order_num), 'get', lambda k: None)
        self.current_wf_state = wf('name') if wf else 'Draft'
        
        c = db.fetch_one("SELECT name FROM customers WHERE customer_id=?", (order['customer_id'],))
        c_name = c['name'] if c else "Unknown"
        
        self.lbl_info.configure(text=f"Invoice #{order['order_number']}  |  Date: {order['order_date']}  |  Customer: {c_name}")
        self.lbl_status_widget = WorkflowStatusLabel(self.info_frame, status=self.current_wf_state)
        self.lbl_status_widget.pack(anchor='w')
        
        items = db.fetch_all("SELECT i.*, p.name FROM sales_order_items i JOIN products p ON i.product_id=p.product_id WHERE order_number=?", (self.order_num,))
        
        rows = []
        for i in items:
            rows.append((
                i['name'], 
                i['quantity'], 
                f"${i['unit_price']:.2f}", 
                f"${i['tax_amount']:.2f}",
                f"${i['discount_amount']:.2f}",
                f"${i['total_price']:.2f}"
            ))
        self.table.set_data(rows)
        
        self.lbl_totals.configure(text=f"Subtotal: ${order['subtotal']:.2f}\nTax: ${order['total_tax']:.2f}\nDiscount: ${order['total_discount']:.2f}\nGrand Total: ${order['total_amount']:.2f}")

        # Store for export
        self.order_data = order
        self.customer_data = {'name': c_name, 'customer_id': order['customer_id']}
        self.items_data = items

        # Actions
        f_actions = tk.Frame(self.content, bg=Theme.BG_WHITE)
        f_actions.pack(fill='x', pady=20)
        
        # PHASE 4: Workflow Actions
        # Standard: Submit if Draft
        if self.current_wf_state == 'Draft':
            ttk.Button(f_actions, text="🚀 Submit Order", style='Success.TButton', command=self.submit_order).pack(side='left', padx=5)
            
        # EMERGENCY FIX: Admin Override
        user_level = self.user_data.get('approval_level', 0)
        # Assuming Level 5 is Admin/Boss
        if user_level and user_level >= 5 and self.current_wf_state not in ['Completed', 'Rejected']:
             ttk.Button(f_actions, text="⚡ Force Complete", style='Danger.TButton', command=self.admin_force_complete).pack(side='left', padx=5)

        ttk.Button(f_actions, text="🖨 Print Invoice", command=self.print_invoice).pack(side='left', padx=5)
        ttk.Button(f_actions, text="💾 Export PDF", command=self.export_pdf).pack(side='left', padx=5)
        ttk.Button(f_actions, text="Close", command=self.destroy).pack(side='right')

    def submit_order(self):
         if messagebox.askyesno("Confirm", "Submit this order for approval?"):
             try:
                 # Assumption: Current user is the rep
                 user_id = self.user_data.get('id')
                 # We need employee_id of current user
                 db = get_db()
                 emp = db.fetch_one("SELECT employee_id FROM employees WHERE user_id=?", (user_id,))
                 if not emp:
                     messagebox.showerror("Error", "You are not linked to an employee record.")
                     return
                 
                 SalesOrderService.submit_order(self.order_num, emp['employee_id'])
                 messagebox.showinfo("Success", "Order Submitted")
                 self.destroy()
                 self.master.load_data()
             except Exception as e:
                 messagebox.showerror("Error", str(e))

    def admin_force_complete(self):
        if messagebox.askyesno("Admin Override", "Force this order to COMPLETED state?\nThis bypasses all checks."):
            try:
                # We need an employee ID. Use current user's linked employee
                db = get_db()
                user_id = self.user_data.get('id')
                emp = db.fetch_one("SELECT employee_id FROM employees WHERE user_id=?", (user_id,))
                emp_id = emp['employee_id'] if emp else 'EMP-001'  # Fallback
                
                # Call fulfill directly (Warehouse function)
                SalesOrderService.fulfill_order(self.order_num, emp_id)
                messagebox.showinfo("Success", "Forced Completion")
                self.destroy()
                self.master.load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def print_invoice(self):
        try:
            # Gen temp file
            path = f"temp_invoice_{self.order_num}.pdf"
            path = os.path.abspath(path)
            
            InvoiceGenerator.generate(path, self.order_data, self.customer_data, self.items_data, self.user_data)
            
            # Print
            # startfile with 'print' verb works on Windows if default PDF reader supports it
            # Otherwise just open it
            try:
                os.startfile(path, 'print')
            except:
                os.startfile(path)
                
        except Exception as e:
            messagebox.showerror("Print Error", str(e))

    def export_pdf(self):
        try:
            fn = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=f"Invoice_{self.order_num}.pdf",
                filetypes=[("PDF Documents", "*.pdf")]
            )
            if not fn: return
            
            InvoiceGenerator.generate(fn, self.order_data, self.customer_data, self.items_data, self.user_data)
            messagebox.showinfo("Export", f"Saved to {fn}")
            
        except Exception as e:
            messagebox.showerror("Export Error", str(e))


class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, order_num, user_data):
        super().__init__(parent)
        self.title("Record Payment")
        self.geometry("450x400")
        Theme.apply_styles(self)
        
        # Make Modal
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        self.order_num = order_num
        self.user_data = user_data
        
        self.content = ttk.Frame(self, style='Main.TFrame', padding=20)
        self.content.pack(fill='both', expand=True)
        
        # Form
        self.amt = tk.StringVar()
        ModernForm(self.content, "Amount ($)", 'entry', variable=self.amt).pack(fill='x', pady=10)
        
        self.method = tk.StringVar(value='Cash')
        ModernForm(self.content, "Payment Method", 'combobox', ['Cash', 'Bank Transfer', 'Credit Card'], variable=self.method).pack(fill='x', pady=10)
        
        ttk.Button(self.content, text="Process Payment", style='Primary.TButton', command=self.save).pack(fill='x', pady=30)
        
    def save(self):
        try:
            amt = float(self.amt.get())
            SalesManager.record_payment(self.order_num, amt, self.method.get(), self.user_data['id'])
            messagebox.showinfo("Success", "Paid")
            self.master.load_data()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class NewCustomerDialog(tk.Toplevel):
    """
    Dialog to create a new Customer.
    """
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.title("New Customer")
        self.geometry("500x500")
        self.configure(bg=Theme.BG_WHITE)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
        # Center
        self.update_idletasks()
        try:
            w, h = self.winfo_width(), self.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (w // 2)
            y = (self.winfo_screenheight() // 2) - (h // 2)
            self.geometry(f'+{int(x)}+{int(y)}')
        except:
            pass

    def setup_ui(self):
        content = tk.Frame(self, bg=Theme.BG_WHITE, padx=30, pady=20)
        content.pack(fill='both', expand=True)
        
        tk.Label(content, text="New Customer", font=("Segoe UI", 16, "bold"), 
                 bg=Theme.BG_WHITE, fg=Theme.PRIMARY).pack(anchor='w', pady=(0, 20))
        
        # Fields
        self.name_var = tk.StringVar()
        ModernForm(content, "Customer Name *", 'entry', variable=self.name_var).pack(fill='x', pady=(0, 10))
        
        self.email_var = tk.StringVar()
        ModernForm(content, "Email", 'entry', variable=self.email_var).pack(fill='x', pady=(0, 10))
        
        self.phone_var = tk.StringVar()
        ModernForm(content, "Phone", 'entry', variable=self.phone_var).pack(fill='x', pady=(0, 10))
        
        self.tax_id_var = tk.StringVar()
        ModernForm(content, "Tax ID / VAT Check", 'entry', variable=self.tax_id_var).pack(fill='x', pady=(0, 20))
        
        # Buttons
        footer = tk.Frame(content, bg=Theme.BG_WHITE)
        footer.pack(fill='x', pady=10)
        
        ttk.Button(footer, text="Cancel", command=self.destroy).pack(side='right', padx=5)
        ttk.Button(footer, text="Create Customer", style='Success.TButton', command=self.save).pack(side='right')

    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Customer name is required")
            return
            
        try:
            db = get_db()
            # Generate ID
            cust_id = "CUST-" + name[:3].upper() + datetime.now().strftime('%M%S')
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.insert('tabCustomer', {
                'name': cust_id,
                'customer_name': name,
                'email_id': self.email_var.get(),
                'mobile_no': self.phone_var.get(),
                'customer_type': 'Individual',
                'customer_group': 'All Customer Groups',
                'territory': 'All Territories',
                'docstatus': 0,
                'owner': 'Administrator',
                'creation': now_str,
                'modified': now_str
            })
            
            # Invalidate cache
            try:
                from modules.lookup_service import LookupService
                LookupService.invalidate_customers()
            except:
                pass
                
            messagebox.showinfo("Success", f"Customer {name} created!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")

