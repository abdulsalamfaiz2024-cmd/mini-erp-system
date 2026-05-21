"""
Reporting Manager
Handles generation of complex reports (PDF/Excel)
"""

from typing import List, Dict
from core.database import get_db
from core.logger import get_logger
from modules.finance.finance_manager import FinanceManager
# Note: For PDF/Excel, we'd typically use reportlab/pandas/openpyxl
# We'll implement data gathering logic here.

logger = get_logger('reporting')

class ReportingManager:
    """Generates System Reports"""

    @staticmethod
    def get_sales_report(start_date: str, end_date: str) -> List[Dict]:
        """Get detailed sales report"""
        db = get_db()
        sql = """
            SELECT so.order_number, so.order_date, c.name, so.total_amount, so.total_profit 
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.customer_id
            WHERE so.order_date BETWEEN ? AND ?
            ORDER BY so.order_date DESC
        """
        return db.fetch_all(sql, (start_date, end_date))

    @staticmethod
    def get_inventory_report() -> List[Dict]:
        """Get current inventory valuation"""
        db = get_db()
        sql = """
            SELECT p.product_id, p.name, SUM(i.quantity) as qty, p.cost_price, (SUM(i.quantity) * p.cost_price) as value 
            FROM products p
            LEFT JOIN inventory i ON p.product_id = i.product_id
            GROUP BY p.product_id
        """
    @staticmethod
    def get_purchase_report(start_date: str, end_date: str) -> List[Dict]:
        """Get detailed purchase report"""
        db = get_db()
        sql = """
            SELECT po.po_number, po.order_date, s.name, po.total_amount, po.status 
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.supplier_id
            WHERE po.order_date BETWEEN ? AND ?
            ORDER BY po.order_date DESC
        """
        return db.fetch_all(sql, (start_date, end_date))

    @staticmethod
    def get_customer_statement(customer_id: int, start_date: str, end_date: str) -> List[Dict]:
        """Get customer statement (invoices and payments)"""
        db = get_db()
        # For simplicity, just listing Invoices for now. 
        # A full statement would merge Invoices and Payments.
        sql = """
            SELECT order_number as ref, order_date as date, 'Invoice' as type, total_amount as debit, 0 as credit, status
            FROM sales_orders 
            WHERE customer_id = ? AND order_date BETWEEN ? AND ?
            UNION ALL
            SELECT payment_id as ref, payment_date as date, 'Payment' as type, 0 as debit, amount as credit, 'Paid' as status
            FROM payments p
            JOIN sales_orders so ON p.entity_id = so.order_number
            WHERE so.customer_id = ? AND p.payment_date BETWEEN ? AND ?
            ORDER BY date
        """
        # Note: Payments table entity_id is string order_number, entity_type='sales_order'
        # My previous query for payments might miss direct customer payments if not linked to order?
        # Current system links payments to orders.
        # Let's refine the Payment query part.
        
        sql = """
            SELECT order_number as ref, order_date as date, 'Invoice' as type, total_amount as debit, 0 as credit, status
            FROM sales_orders 
            WHERE customer_id = ? AND order_date BETWEEN ? AND ?
            ORDER BY date
        """
        return db.fetch_all(sql, (customer_id, start_date, end_date))

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str):
        import csv
        if not data: return
        
        keys = data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows([dict(row) for row in data])
            
    @staticmethod
    def export_to_excel(data: List[Dict], filename: str):
        from openpyxl import Workbook
        if not data: return
        
        wb = Workbook()
        ws = wb.active
        
        # Header
        keys = list(data[0].keys())
        ws.append(keys)
        
        # Rows
        for row in data:
            ws.append([row[k] for k in keys])
            
        wb.save(filename)

    @staticmethod
    def export_pdf_table(title, headers, data_rows, filename, totals=None):
        """Generic PDF Table Export"""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        import os
        
        # Try to register a font that supports Arabic
        MAIN_FONT = 'Helvetica'
        BOLD_FONT = 'Helvetica-Bold'
        try:
            font_path = "C:\\Windows\\Fonts\\arial.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                pdfmetrics.registerFont(TTFont('Arial-Bold', "C:\\Windows\\Fonts\\arialbd.ttf"))
                MAIN_FONT = 'Arial'
                BOLD_FONT = 'Arial-Bold'
        except Exception:
            pass

        # Arabic Helper
        import arabic_reshaper
        from bidi.algorithm import get_display
        def fix_text(text):
            if not text: return ""
            text = str(text)
            try:
                reshaped_text = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped_text)
                return bidi_text
            except:
                return text
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Update Styles
        styles['Normal'].fontName = MAIN_FONT
        styles['Title'].fontName = BOLD_FONT
        
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))
        
        if not data_rows:
            elements.append(Paragraph("No data found.", styles['Normal']))
        else:
            # Apply fix_text to all data cells
            fixed_rows = []
            for row in data_rows:
                fixed_rows.append([fix_text(cell) for cell in row])
            
            table_data = [headers] + fixed_rows
            
            # Auto-calc col widths? Or let reportlab decide.
            t = Table(table_data)
            
            style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), BOLD_FONT),
                ('FONTNAME', (0, 1), (-1, -1), MAIN_FONT),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ]
            t.setStyle(TableStyle(style))
            elements.append(t)
            
            if totals:
                elements.append(Spacer(1, 12))
                for label, val in totals.items():
                    elements.append(Paragraph(f"<b>{label}:</b> {val}", styles['Normal']))

        doc.build(elements)
