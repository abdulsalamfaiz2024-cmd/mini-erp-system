"""
Assets Page
Manage company assets with depreciation tracking
"""

from tkinter import ttk, messagebox
from ui.layout.base_page import BasePage
from ui.modern_widgets import ModernTable
from core.database import get_db


class AssetsPage(BasePage):
    """Assets management page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Assets")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'Register Asset',
                'command': self.register_asset,
                'icon': '➕',
                'style': 'Success.TButton'
            },
            {
                'text': 'Depreciate',
                'command': self.depreciate_asset,
                'icon': '📉',
                'enabled': False,
                'tooltip': 'Select an active asset first'
            },
            {
                'text': 'Dispose',
                'command': self.dispose_asset,
                'icon': '🗑️',
                'enabled': False,
                'tooltip': 'Select an asset to dispose'
            },
            {'type': 'separator'},
            {
                'text': 'Refresh',
                'command': self.refresh,
                'icon': '🔄'
            }
        ])
    
    def setup_content(self):
        """Build page content"""
        table_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=20)
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            table_frame,
            text="🏢 Company Assets",
            style='CardTitle.TLabel',
            font=('Segoe UI', 14, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        cols = [
            {'name': 'asset_id', 'text': 'Asset ID', 'width': 100},
            {'name': 'name', 'text': 'Name', 'width': 200},
            {'name': 'category', 'text': 'Category', 'width': 120},
            {'name': 'purchase_date', 'text': 'Purchase Date', 'width': 110},
            {'name': 'cost', 'text': 'Cost', 'width': 100, 'anchor': 'e'},
            {'name': 'book_value', 'text': 'Book Value', 'width': 100, 'anchor': 'e'},
            {'name': 'status', 'text': 'Status', 'width': 100},
        ]
        
        self.table = ModernTable(table_frame, cols)
        self.table.pack(fill='both', expand=True)
        
        # Enable row selection
        self.table.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def load_data(self):
        """Load assets data"""
        db = get_db()
        
        # Check if table exists
        try:
            sql = """
                SELECT a.asset_id, a.name, a.category, a.purchase_date, 
                       a.purchase_cost, a.book_value,
                       ws.name as status
                FROM assets a
                LEFT JOIN document_state_tracker dst ON dst.document_id = a.asset_id
                LEFT JOIN workflow_states ws ON dst.current_state_id = ws.state_id
                WHERE dst.document_type = 'ASSET' OR dst.document_type IS NULL
                ORDER BY a.purchase_date DESC
                LIMIT 100
            """
            
            rows = db.fetch_all(sql)
            
            display_data = []
            for row in rows:
                display_data.append((
                    row['asset_id'],
                    row['name'],
                    row['category'] or 'N/A',
                    row['purchase_date'],
                    f"${row['purchase_cost']:,.2f}" if row['purchase_cost'] else '$0.00',
                    f"${row['book_value']:,.2f}" if row['book_value'] else '$0.00',
                    row['status'] or 'Active'
                ))
            
            self.table.set_data(display_data)
        except Exception as e:
            # Table might not exist yet
            self.table.set_data([])
    
    def _on_select(self, event=None):
        """Handle row selection - enable/disable buttons"""
        selected = self.table.get_selected()
        # Would update button states based on asset status
        pass
    
    def register_asset(self):
        """
        Register new asset
        API: AssetService.register_asset
        """
        messagebox.showinfo(
            "Register Asset",
            "Asset registration dialog will be implemented.\n\n"
            "API: AssetService.register_asset\n"
            "Workflow: ASSET → Active state"
        )
    
    def depreciate_asset(self):
        """
        Apply depreciation to asset
        API: AssetService.depreciate_asset (TO BE IMPLEMENTED)
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an asset first")
            return
        
        asset_id = selected['values'][0]
        
        messagebox.showinfo(
            "Depreciate Asset",
            f"Depreciation for asset {asset_id} will be implemented.\n\n"
            "API: AssetService.depreciate_asset\n"
            "Status: Pending implementation"
        )
    
    def dispose_asset(self):
        """
        Dispose of asset
        API: AssetService.dispose_asset (TO BE IMPLEMENTED)
        """
        selected = self.table.get_selected()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an asset first")
            return
        
        asset_id = selected['values'][0]
        
        messagebox.showinfo(
            "Dispose Asset",
            f"Disposal of asset {asset_id} will be implemented.\n\n"
            "API: AssetService.dispose_asset\n"
            "Status: Pending implementation"
        )
