"""
Reports Page
Report generation interface using BasePage pattern
"""

from tkinter import ttk, filedialog, messagebox
from ui.layout.base_page import BasePage
from modules.reporting.reporting_manager import ReportingManager
import tkinter as tk


class ReportsPage(BasePage):
    """Reports page"""
    
    def __init__(self, parent, user_data):
        super().__init__(parent, user_data, page_title="Reports")
    
    def setup_actions(self):
        """Setup top action bar"""
        self.topbar.set_actions([
            {
                'text': 'Sales Report',
                'command': self.generate_sales_report,
                'icon': '📊'
            },
            {
                'text': 'Inventory Report',
                'command': self.generate_inventory_report,
                'icon': '📦'
            },
            {
                'text': 'Export CSV',
                'command': self.export_csv,
                'icon': '📑'
            }
        ])
    
    def setup_content(self):
        """Build page content"""
        info_frame = ttk.Frame(self.content_frame, style='Card.TFrame', padding=40)
        info_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(
            info_frame,
            text="📈 Reports & Analytics",
            style='CardTitle.TLabel',
            font=('Segoe UI', 18, 'bold')
        ).pack(pady=(0, 20))
        
        self.report_text = tk.Text(
            info_frame,
            height=20,
            width=80,
            font=('Consolas', 10),
            wrap='word'
        )
        self.report_text.pack(fill='both', expand=True)
        
    def load_data(self):
        """Initial load"""
        self.report_text.insert('1.0', "Select a report from the top bar to generate...")
    
    def generate_sales_report(self):
        """Generate sales report"""
        report = self.call_api(
            "ReportingManager.get_sales_report",
            ReportingManager.get_sales_report
        )
        
        if report:
            self.report_text.delete('1.0', 'end')
            self.report_text.insert('1.0', str(report))
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        report = self.call_api(
            "ReportingManager.get_inventory_report",
            ReportingManager.get_inventory_report
        )
        
        if report:
            self.report_text.delete('1.0', 'end')
            self.report_text.insert('1.0', str(report))
    
    def export_csv(self):
        """Export current report to CSV"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if filepath:
            try:
                content = self.report_text.get('1.0', 'end')
                with open(filepath, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
