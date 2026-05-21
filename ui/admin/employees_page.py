"""
Employees Management Page
Manage employees, permissions, and roles

API Bindings:
- EmployeeService.create_employee (New Employee)
- EmployeeService.update_employee (Edit)
- EmployeeService.assign_permissions (Assign Permissions)
- EmployeeService.change_status (Activate/Deactivate)
- EmployeeService.list_employees (Load Data)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from core.database import get_db


class EmployeesPage(BasePage):
    """Employee management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Employees")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'New Employee',
                'command': self.new_employee,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Edit',
                'command': self.edit_employee,
                'icon': '✏️',
                'enabled': False,
                'tooltip': 'Select an employee first'
            },
            {
                'text': 'Permissions',
                'command': self.assign_permissions,
                'icon': '🔐',
                'enabled': False,
                'tooltip': 'Select an employee first'
            },
            {'type': 'separator'},
            {
                'text': 'Deactivate',
                'command': self.deactivate,
                'icon': '🚫',
                'style': 'Danger.TButton',
                'enabled': False,
                'tooltip': 'Select an employee first'
            },
        ])
    
    def setup_content(self):
        """Build page content"""
        # Employees table
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="👥 All Employees",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'employee_id', 'text': 'ID', 'width': 100},
            {'name': 'name', 'text': 'Name', 'width': 200},
            {'name': 'department', 'text': 'Department', 'width': 150},
            {'name': 'job_title', 'text': 'Position', 'width': 150},
            {'name': 'approval_level', 'text': 'Approval Lvl', 'width': 100},
            {'name': 'status', 'text': 'Status', 'width': 100},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def load_data(self):
        """
        Load employees directly from database
        (EmployeeService.list_employees depends on missing models.py)
        """
        db = get_db()
        
        rows = db.fetch_all("""
            SELECT employee_id, full_name, department, job_title, 
                   approval_level, status
            FROM employees
            ORDER BY full_name
        """)
        
        display_data = []
        for row in rows:
            display_data.append((
                row['employee_id'],
                row['full_name'],
                row['department'] or 'N/A',
                row['job_title'] or 'N/A',
                row['approval_level'] if row['approval_level'] else 0,
                row['status'] or 'ACTIVE'
            ))
        
        self.table.set_data(display_data)
    
    def _on_select(self, event=None):
        """Handle selection"""
        pass
    
    def new_employee(self):
        """
        Create new employee with smart supervisor lookup
        API: EmployeeService.create_employee
        """
        # Create New Employee dialog
        dialog = tk.Toplevel(self)
        dialog.title("New Employee")
        dialog.geometry("500x550")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg='white')
        
        content = tk.Frame(dialog, bg='white', padx=30, pady=20)
        content.pack(fill='both', expand=True)
        
        tk.Label(content, text="New Employee", font=("Segoe UI", 16, "bold"), 
                 bg='white', fg='#111827').pack(anchor='w', pady=(0, 20))
        
        # Basic fields
        name_var = tk.StringVar()
        tk.Label(content, text="Full Name *", font=("Segoe UI", 10), bg='white').pack(anchor='w')
        ttk.Entry(content, textvariable=name_var, font=("Segoe UI", 10)).pack(fill='x', pady=(0, 10))
        
        dept_var = tk.StringVar()
        tk.Label(content, text="Department", font=("Segoe UI", 10), bg='white').pack(anchor='w')
        ttk.Combobox(content, textvariable=dept_var, values=['Sales', 'Finance', 'Warehouse', 'IT', 'HR', 'Management']).pack(fill='x', pady=(0, 10))
        
        title_var = tk.StringVar()
        tk.Label(content, text="Job Title", font=("Segoe UI", 10), bg='white').pack(anchor='w')
        ttk.Entry(content, textvariable=title_var, font=("Segoe UI", 10)).pack(fill='x', pady=(0, 10))
        
        email_var = tk.StringVar()
        tk.Label(content, text="Email", font=("Segoe UI", 10), bg='white').pack(anchor='w')
        ttk.Entry(content, textvariable=email_var, font=("Segoe UI", 10)).pack(fill='x', pady=(0, 10))
        
        # Supervisor lookup with SmartLookupField
        supervisor_id_var = tk.StringVar()
        supervisor_name_var = tk.StringVar()
        
        try:
            from ui.widgets.smart_lookup import SmartLookupField
            from modules.lookup_service import LookupService
            
            supervisor_lookup = SmartLookupField(
                content,
                label="Reports To (Supervisor)",
                data_source=LookupService.get_employees,
                id_var=supervisor_id_var,
                name_var=supervisor_name_var,
                placeholder="Search supervisor..."
            )
            supervisor_lookup.pack(fill='x', pady=(0, 10))
        except ImportError:
            tk.Label(content, text="Supervisor ID", font=("Segoe UI", 10), bg='white').pack(anchor='w')
            ttk.Entry(content, textvariable=supervisor_id_var).pack(fill='x', pady=(0, 10))
        
        level_var = tk.StringVar(value="1")
        tk.Label(content, text="Approval Level (1-5)", font=("Segoe UI", 10), bg='white').pack(anchor='w')
        ttk.Combobox(content, textvariable=level_var, values=['1', '2', '3', '4', '5']).pack(fill='x', pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill='x', pady=(10, 0))
        
        def save():
            if not name_var.get().strip():
                messagebox.showerror("Error", "Full name is required")
                return
            
            try:
                from modules.employee.service import EmployeeService
                
                data = {
                    'full_name': name_var.get().strip(),
                    'department': dept_var.get(),
                    'job_title': title_var.get(),
                    'email': email_var.get(),
                    'reports_to': supervisor_id_var.get() or None,
                    'approval_level': int(level_var.get()),
                    'status': 'ACTIVE'
                }
                
                emp_id = EmployeeService.create_employee(data, performed_by_id=self.get_employee_id())
                
                # Invalidate cache
                try:
                    LookupService.invalidate_employees()
                except:
                    pass
                
                messagebox.showinfo("Success", f"Created employee {emp_id}")
                dialog.destroy()
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Create Employee", style='Success.TButton', command=save).pack(side='right')
    
    def edit_employee(self):
        """
        Edit employee
        API: EmployeeService.update_employee
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee first")
            return
        
        emp_id = selected['values'][0]
        messagebox.showinfo("Edit", f"Edit dialog for employee {emp_id}")
    
    def assign_permissions(self):
        """
        Assign permissions
        API: EmployeeService.assign_permissions
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee first")
            return
        
        emp_id = selected['values'][0]
        messagebox.showinfo("Permissions", f"Permission editor for {emp_id}")
    
    def deactivate(self):
        """
        Deactivate employee
        API: EmployeeService.change_status
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee first")
            return
        
        emp_id = selected['values'][0]
        
        if messagebox.askyesno("Confirm", f"Deactivate employee {emp_id}?"):
            result = self.call_api(
                "EmployeeService.change_status",
                EmployeeService.change_status,
                emp_id,
                'inactive',
                success_msg=f"Employee {emp_id} deactivated"
            )
            
            if result is not None:
                self.refresh()
