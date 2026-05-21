"""
Chart widgets using matplotlib for dashboard
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from core.database import get_db
from ui.styles import Theme


class SalesChart(ttk.Frame):
    """Sales trend chart"""
    
    def __init__(self, parent, days=30):
        super().__init__(parent, style='Card.TFrame')
        self.days = days
        
        # Title
        ttk.Label(self, text="Sales Trend (30 Days)", style='CardTitle.TLabel', 
                 padding=15).pack(anchor='w')
        
        # Create chart
        self.create_chart()
    
    def create_chart(self):
        """Create matplotlib chart"""
        db = get_db()
        
        # Get data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)
        
        data = db.fetch_all(
            """SELECT DATE(order_date) as date, SUM(total_amount) as total
               FROM sales_orders
               WHERE order_date >= ? AND order_date <= ?
               GROUP BY DATE(order_date)
               ORDER BY date""",
            (start_date.date().isoformat(), end_date.date().isoformat())
        )
        
        # Prepare data
        if data:
            dates = [row['date'] for row in data]
            amounts = [row['total'] for row in data]
        else:
            dates = []
            amounts = []
        
        # Create figure
        fig = Figure(figsize=(6, 3), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        if dates:
            ax.plot(dates, amounts, color='#3498DB', linewidth=2, marker='o', markersize=4)
            ax.fill_between(range(len(dates)), amounts, alpha=0.3, color='#3498DB')
        
        ax.set_xlabel('Date', fontsize=9)
        ax.set_ylabel('Sales ($)', fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=8)
        
        # Rotate x labels
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=(0, 15))


class ProductsChart(ttk.Frame):
    """Top products bar chart"""
    
    def __init__(self, parent, limit=10):
        super().__init__(parent, style='Card.TFrame')
        self.limit = limit
        
        # Title
        ttk.Label(self, text=f"Top {limit} Products", style='CardTitle.TLabel',
                 padding=15).pack(anchor='w')
        
        # Create chart
        self.create_chart()
    
    def create_chart(self):
        """Create bar chart"""
        db = get_db()
        
        # Get top products
        data = db.fetch_all(
            """SELECT p.name, COUNT(*) as sold
               FROM products p
               WHERE p.deleted_at IS NULL
               GROUP BY p.product_id
               ORDER BY sold DESC
               LIMIT ?""",
            (self.limit,)
        )
        
        if data:
            products = [row['name'][:20] for row in data]  # Truncate names
            quantities = [row['sold'] for row in data]
        else:
            products = ['No Data']
            quantities = [0]
        
        # Create figure
        fig = Figure(figsize=(6, 3), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        bars = ax.barh(products, quantities, color='#27AE60')
        ax.set_xlabel('Quantity Sold', fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.3, axis='x', linestyle='--')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center', fontsize=8, 
                   fontweight='bold')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=(0, 15))


class StockChart(ttk.Frame):
    """Stock status pie chart"""
    
    def __init__(self, parent):
        super().__init__(parent, style='Card.TFrame')
        
        # Title
        ttk.Label(self, text="Stock Status", style='CardTitle.TLabel',
                 padding=15).pack(anchor='w')
        
        # Create chart
        self.create_chart()
    
    def create_chart(self):
        """Create pie chart"""
        db = get_db()
        
        # Get stock status
        in_stock = db.fetch_one(
            """SELECT COUNT(*) as count FROM products p
               LEFT JOIN inventory i ON p.product_id = i.product_id
               WHERE p.deleted_at IS NULL
               GROUP BY p.product_id
               HAVING SUM(COALESCE(i.quantity, 0)) > 10"""
        )
        
        low_stock = db.fetch_one(
            """SELECT COUNT(*) as count FROM products p
               LEFT JOIN inventory i ON p.product_id = i.product_id
               WHERE p.deleted_at IS NULL
               GROUP BY p.product_id
               HAVING SUM(COALESCE(i.quantity, 0)) BETWEEN 1 AND 10"""
        )
        
        out_of_stock = db.fetch_one(
            """SELECT COUNT(*) as count FROM products p
               LEFT JOIN inventory i ON p.product_id = i.product_id
               WHERE p.deleted_at IS NULL
               GROUP BY p.product_id
               HAVING SUM(COALESCE(i.quantity, 0)) = 0"""
        )
        
        labels = ['In Stock', 'Low Stock', 'Out of Stock']
        sizes = [
            in_stock['count'] if in_stock else 0,
            low_stock['count'] if low_stock else 0,
            out_of_stock['count'] if out_of_stock else 0
        ]
        colors = ['#27AE60', '#F39C12', '#C0392B']
        
        # Create figure
        fig = Figure(figsize=(4, 3), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        
        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                  startangle=90, textprops={'fontsize': 9})
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center',
                   fontsize=12, transform=ax.transAxes)
        
        ax.axis('equal')
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=15, pady=(0, 15))
