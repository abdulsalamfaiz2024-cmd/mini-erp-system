import tkinter as tk
from tkinter import ttk, messagebox
from ui.modern_widgets import ModernTable
from ui.styles import Theme

class WorkflowStatusLabel(ttk.Label):
    """
    Color-coded label for Workflow Status.
    """
    COLORS = {
        'Draft': '#6c757d', # Gray
        'Submitted': '#0d6efd', # Blue
        'Finance_Approved': '#fd7e14', # Orange
        'Ready_For_Warehouse': '#6f42c1', # Purple
        'Completed': '#198754', # Green
        'Rejected': '#dc3545'  # Red
    }
    
    def __init__(self, parent, status='Draft', **kwargs):
        super().__init__(parent, text=status, font=('Segoe UI', 10, 'bold'), **kwargs)
        self.set_status(status)
        
    def set_status(self, status):
        # Normalize status string
        normalized = status.replace(' ', '_')
        color = self.COLORS.get(normalized, '#333333')
        self.configure(text=status.replace('_', ' '), foreground=color)

class PendingActionsWidget(ttk.Frame):
    """
    A widget to list documents requiring action.
    cols: List of dicts for table columns.
    on_approve: Callback(document_id)
    on_reject: Callback(document_id)
    on_view: Callback(document_id)
    """
    def __init__(self, parent, title="Pending Actions", cols=None, on_approve=None, on_reject=None, on_view=None, approve_text="✅ Approve / Release", reject_text="❌ Reject"):
        super().__init__(parent, style='Card.TFrame', padding=15)
        self.on_approve = on_approve
        self.on_reject = on_reject
        self.on_view = on_view
        
        # Header
        h = ttk.Frame(self)
        h.pack(fill='x', pady=(0, 10))
        ttk.Label(h, text=title, style='CardTitle.TLabel').pack(side='left')
        ttk.Button(h, text="🔄 Refresh", command=self.load_data, style='Secondary.TButton').pack(side='right')
        
        # Table
        default_cols = [
            {'name': 'id', 'text': 'ID', 'width': 100},
            {'name': 'date', 'text': 'Date', 'width': 100},
            {'name': 'desc', 'text': 'Description', 'width': 200},
            {'name': 'state', 'text': 'State', 'width': 120},
        ]
        self.table_cols = cols or default_cols
        self.table = ModernTable(self, self.table_cols)
        self.table.pack(fill='both', expand=True, pady=(0, 10))
        
        # Actions Row
        actions = ttk.Frame(self)
        actions.pack(fill='x')
        
        if on_view:
            ttk.Button(actions, text="👁 View", command=self._handle_view).pack(side='left', padx=(0, 5))
        
        if on_approve or on_reject:
            # Right align action buttons
            if on_reject:
                ttk.Button(actions, text=reject_text, command=self._handle_reject, style='Danger.TButton').pack(side='right', padx=(5, 0))
            if on_approve:
                ttk.Button(actions, text=approve_text, command=self._handle_approve, style='Success.TButton').pack(side='right')
                
        self.loader_func = None

    def set_loader(self, loader_func):
        """
        loader_func: Callable returning list of tuples matching cols
        """
        self.loader_func = loader_func
        self.load_data()

    def load_data(self):
        if self.loader_func:
            try:
                data = self.loader_func()
                self.table.set_data(data)
            except Exception as e:
                print(f"Error loading pending actions: {e}")
                
    def _get_selected_id(self):
        item = self.table.get_selected()
        if not item:
            messagebox.showwarning("Selection", "Please select an item first.")
            return None
        # Assuming ID is first column
        return item['values'][0]

    def _handle_approve(self):
        doc_id = self._get_selected_id()
        if doc_id and self.on_approve:
            self.on_approve(doc_id)
            self.load_data()

    def _handle_reject(self):
        doc_id = self._get_selected_id()
        if doc_id and self.on_reject:
            self.on_reject(doc_id)
            self.load_data()

    def _handle_view(self):
        doc_id = self._get_selected_id()
        if doc_id and self.on_view:
            self.on_view(doc_id)
