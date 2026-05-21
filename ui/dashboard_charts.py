"""
Dashboard Charts Widget
Provides interactive charts for the executive dashboard using matplotlib
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import List, Dict, Any
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

from core.database import get_db
from core.logger import get_logger
from ui.styles import Theme

logger = get_logger('dashboard_charts')


class ChartWidget(ttk.Frame):
    """Base class for chart widgets"""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        self.figure = None
        self.canvas = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup chart UI"""
        # Title
        title_frame = ttk.Frame(self, style='Card.TFrame')
        title_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(
            title_frame,
            text=self.title,
            style='H2.TLabel',
            font=('Arial', 12, 'bold')
        ).pack(side='left', padx=10)
        
        # Chart area
        self.chart_frame = ttk.Frame(self, style='Card.TFrame')
        self.chart_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_figure(self, figsize=(6, 4)):
        """Create matplotlib figure"""
        self.figure = Figure(figsize=figsize, dpi=80, facecolor='#FFFFFF')
        self.canvas = FigureCanvasTkAgg(self.figure, self.chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        return self.figure
    
    def refresh(self):
        """Refresh chart data - override in subclasses"""
        pass


class SalesTrendChart(ChartWidget):
    """Sales trend chart showing daily sales over time"""
    
    def __init__(self, parent, days: int = 30, **kwargs):
        self.days = days
        super().__init__(parent, f"Sales Trend (Last {days} Days)", **kwargs)
        self.refresh()
    
    def refresh(self):
        """Load and display sales trend data"""
        try:
            db = get_db()
            
            # Get sales data for last N days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=self.days)
            
            query = """
                SELECT DATE(order_date) as date, SUM(total_amount) as total
                FROM sales_orders
                WHERE order_date BETWEEN ? AND ?
                AND status IN ('invoiced', 'paid', 'completed')
                GROUP BY DATE(order_date)
                ORDER BY date
            """
            
            rows = db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
            
            if not rows:
                self._show_no_data()
                return
            
            # Prepare data
            dates = [datetime.strptime(row['date'], '%Y-%m-%d') for row in rows]
            amounts = [row['total'] for row in rows]
            
            # Create chart
            fig = self.create_figure(figsize=(7, 3.5))
            ax = fig.add_subplot(111)
            
            # Plot line chart
            ax.plot(dates, amounts, marker='o', linewidth=2, markersize=4, color='#3498db')
            ax.fill_between(dates, amounts, alpha=0.3, color='#3498db')
            
            # Formatting
            ax.set_xlabel('Date', fontsize=9)
            ax.set_ylabel('Sales Amount', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(labelsize=8)
            
            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, self.days // 10)))
            fig.autofmt_xdate()
            
            fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Failed to load sales trend: {e}", exc_info=True)
            self._show_error()
    
    def _show_no_data(self):
        """Show no data message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No sales data available', 
                ha='center', va='center', fontsize=12, color='#7f8c8d')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
    def _show_error(self):
        """Show error message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Error loading chart', 
                ha='center', va='center', fontsize=12, color='#e74c3c')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()


class TopProductsChart(ChartWidget):
    """Bar chart showing top selling products"""
    
    def __init__(self, parent, limit: int = 10, **kwargs):
        self.limit = limit
        super().__init__(parent, f"Top {limit} Products", **kwargs)
        self.refresh()
    
    def refresh(self):
        """Load and display top products"""
        try:
            db = get_db()
            
            query = """
                SELECT p.name, SUM(soi.quantity) as total_qty, SUM(soi.total_price) as total_sales
                FROM sales_order_items soi
                JOIN products p ON soi.product_id = p.product_id
                JOIN sales_orders so ON soi.order_number = so.order_number
                WHERE so.status IN ('invoiced', 'paid', 'completed')
                GROUP BY p.product_id
                ORDER BY total_sales DESC
                LIMIT ?
            """
            
            rows = db.fetch_all(query, (self.limit,))
            
            if not rows:
                self._show_no_data()
                return
            
            # Prepare data
            products = [row['name'][:20] + '...' if len(row['name']) > 20 else row['name'] 
                       for row in rows]
            sales = [row['total_sales'] for row in rows]
            
            # Create chart
            fig = self.create_figure(figsize=(7, 4))
            ax = fig.add_subplot(111)
            
            # Horizontal bar chart
            y_pos = range(len(products))
            bars = ax.barh(y_pos, sales, color='#2ecc71', alpha=0.8)
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, sales)):
                ax.text(value, i, f' {value:,.0f}', 
                       va='center', fontsize=8, color='#2c3e50')
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(products, fontsize=8)
            ax.set_xlabel('Total Sales', fontsize=9)
            ax.grid(True, axis='x', alpha=0.3, linestyle='--')
            
            fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Failed to load top products: {e}", exc_info=True)
            self._show_error()
    
    def _show_no_data(self):
        """Show no data message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No product data available', 
                ha='center', va='center', fontsize=12, color='#7f8c8d')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
    def _show_error(self):
        """Show error message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Error loading chart', 
                ha='center', va='center', fontsize=12, color='#e74c3c')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()


class InventoryStatusChart(ChartWidget):
    """Pie chart showing inventory status"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, "Inventory Status", **kwargs)
        self.refresh()
    
    def refresh(self):
        """Load and display inventory status"""
        try:
            db = get_db()
            
            # Get inventory levels
            query = """
                SELECT 
                    p.product_id,
                    p.name,
                    p.reorder_level,
                    p.min_stock_level,
                    COALESCE(SUM(i.quantity), 0) as current_stock
                FROM products p
                LEFT JOIN inventory i ON p.product_id = i.product_id
                WHERE p.status = 'active'
                GROUP BY p.product_id
            """
            
            rows = db.fetch_all(query)
            
            if not rows:
                self._show_no_data()
                return
            
            # Categorize products
            healthy = sum(1 for r in rows if r['current_stock'] > r['reorder_level'])
            low_stock = sum(1 for r in rows if r['min_stock_level'] < r['current_stock'] <= r['reorder_level'])
            out_of_stock = sum(1 for r in rows if r['current_stock'] <= r['min_stock_level'])
            
            # Create chart
            fig = self.create_figure(figsize=(5, 3.5))
            ax = fig.add_subplot(111)
            
            sizes = [healthy, low_stock, out_of_stock]
            labels = [f'Healthy ({healthy})', f'Low Stock ({low_stock})', f'Out of Stock ({out_of_stock})']
            colors = ['#2ecc71', '#f39c12', '#e74c3c']
            explode = (0.05, 0.05, 0.1)
            
            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
            ax.axis('equal')
            
            fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Failed to load inventory status: {e}", exc_info=True)
            self._show_error()
    
    def _show_no_data(self):
        """Show no data message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No inventory data available', 
                ha='center', va='center', fontsize=12, color='#7f8c8d')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
    def _show_error(self):
        """Show error message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Error loading chart', 
                ha='center', va='center', fontsize=12, color='#e74c3c')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()


class ProfitMarginChart(ChartWidget):
    """Line chart showing profit margin trend"""
    
    def __init__(self, parent, days: int = 30, **kwargs):
        self.days = days
        super().__init__(parent, f"Profit Margin Trend (Last {days} Days)", **kwargs)
        self.refresh()
    
    def refresh(self):
        """Load and display profit margin trend"""
        try:
            db = get_db()
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=self.days)
            
            query = """
                SELECT 
                    DATE(order_date) as date,
                    SUM(total_amount) as revenue,
                    SUM(total_cost) as cost,
                    SUM(total_profit) as profit
                FROM sales_orders
                WHERE order_date BETWEEN ? AND ?
                AND status IN ('invoiced', 'paid', 'completed')
                GROUP BY DATE(order_date)
                ORDER BY date
            """
            
            rows = db.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
            
            if not rows:
                self._show_no_data()
                return
            
            # Calculate profit margin percentage
            dates = [datetime.strptime(row['date'], '%Y-%m-%d') for row in rows]
            margins = [(row['profit'] / row['revenue'] * 100) if row['revenue'] > 0 else 0 
                      for row in rows]
            
            # Create chart
            fig = self.create_figure(figsize=(7, 3.5))
            ax = fig.add_subplot(111)
            
            ax.plot(dates, margins, marker='o', linewidth=2, markersize=4, color='#9b59b6')
            ax.fill_between(dates, margins, alpha=0.3, color='#9b59b6')
            
            ax.set_xlabel('Date', fontsize=9)
            ax.set_ylabel('Profit Margin (%)', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(labelsize=8)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, self.days // 10)))
            fig.autofmt_xdate()
            
            # Add average line
            avg_margin = sum(margins) / len(margins) if margins else 0
            ax.axhline(y=avg_margin, color='#e74c3c', linestyle='--', 
                      linewidth=1, label=f'Avg: {avg_margin:.1f}%')
            ax.legend(fontsize=8)
            
            fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Failed to load profit margin: {e}", exc_info=True)
            self._show_error()
    
    def _show_no_data(self):
        """Show no data message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No profit data available', 
                ha='center', va='center', fontsize=12, color='#7f8c8d')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
    
    def _show_error(self):
        """Show error message"""
        fig = self.create_figure()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Error loading chart', 
                ha='center', va='center', fontsize=12, color='#e74c3c')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()
