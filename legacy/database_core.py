import sqlite3
import pandas as pd
from datetime import datetime
import os


class TailoredDatabase:
    """قاعدة البيانات المخصصة لملف Excel الخاص بك"""

    def __init__(self):
        self.conn = sqlite3.connect('perfect_sales_system.db')
        self.create_tailored_tables()

    def create_tailored_tables(self):
        """إنشاء جداول تطابق تماماً هيكل ملف Excel"""
        cursor = self.conn.cursor()

        # جدول العملاء - من أعمدة الجهة
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS customers
                       (
                           customer_id
                           TEXT
                           PRIMARY
                           KEY,
                           name
                           TEXT
                           NOT
                           NULL,
                           customer_type
                           TEXT,
                           phone
                           TEXT,
                           email
                           TEXT,
                           address
                           TEXT,
                           created_date
                           DATE,
                           notes
                           TEXT
                       )
                       ''')

        # جدول المنتجات - من ورقة الرئيسية
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products
                       (
                           product_id
                           TEXT
                           PRIMARY
                           KEY,
                           name
                           TEXT
                           NOT
                           NULL,
                           category
                           TEXT,
                           cost_price
                           REAL
                           DEFAULT
                           0,
                           selling_price
                           REAL
                           DEFAULT
                           0,
                           initial_quantity
                           INTEGER
                           DEFAULT
                           0,
                           quantity_sold
                           INTEGER
                           DEFAULT
                           0,
                           current_stock
                           INTEGER
                           DEFAULT
                           0,
                           min_stock_level
                           INTEGER
                           DEFAULT
                           0,
                           notes
                           TEXT,
                           last_updated
                           DATE
                       )
                       ''')

        # جدول المبيعات - من ورقة المبيعات
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS sales
                       (
                           sale_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           invoice_number
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           customer_id
                           TEXT,
                           sale_date
                           DATE,
                           total_amount
                           REAL
                           DEFAULT
                           0,
                           paid_amount
                           REAL
                           DEFAULT
                           0,
                           remaining_amount
                           REAL
                           DEFAULT
                           0,
                           payment_status
                           TEXT,
                           notes
                           TEXT,
                           created_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           customer_id
                       ) REFERENCES customers
                       (
                           customer_id
                       )
                           )
                       ''')

        # جدول عناصر الفواتير - من ورقة الفواتير
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS invoice_items
                       (
                           item_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           invoice_number
                           TEXT,
                           customer_id
                           TEXT,
                           product_id
                           TEXT,
                           quantity
                           INTEGER
                           DEFAULT
                           0,
                           unit_price
                           REAL
                           DEFAULT
                           0,
                           total_price
                           REAL
                           DEFAULT
                           0,
                           line_number
                           INTEGER,
                           created_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           invoice_number
                       ) REFERENCES sales
                       (
                           invoice_number
                       ),
                           FOREIGN KEY
                       (
                           customer_id
                       ) REFERENCES customers
                       (
                           customer_id
                       ),
                           FOREIGN KEY
                       (
                           product_id
                       ) REFERENCES products
                       (
                           product_id
                       )
                           )
                       ''')

        # جدول التحصيلات - من ورقة التحصيلات
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS collections
                       (
                           collection_id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           customer_id
                           TEXT,
                           collection_date
                           DATE,
                           amount
                           REAL
                           DEFAULT
                           0,
                           description
                           TEXT,
                           created_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           customer_id
                       ) REFERENCES customers
                       (
                           customer_id
                       )
                           )
                       ''')

        self.conn.commit()

    def execute_query(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetch_all(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()


class DataProcessor:
    """معالج البيانات للتحويل بين Excel وقاعدة البيانات"""

    @staticmethod
    def safe_float_conversion(value):
        """تحويل آمن إلى رقم عشري مع معالجة الصيغ المختلفة"""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def safe_int_conversion(value):
        """تحويل آمن إلى عدد صحيح مع معالجة الصيغ المختلفة"""
        if pd.isna(value) or value == '' or value is None:
            return 0
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return int(float(value))
        except (ValueError, TypeError):
            return 0


class SalesCalculator:
    """آلة حاسبة للمبيعات والتكاليف والأرباح"""

    @staticmethod
    def calculate_total_cost(quantity, unit_cost):
        return quantity * unit_cost

    @staticmethod
    def calculate_total_sales(quantity_sold, unit_price):
        return quantity_sold * unit_price

    @staticmethod
    def calculate_net_profit(total_sales, cost_of_sales):
        return total_sales - cost_of_sales

    @staticmethod
    def calculate_profit_per_unit(selling_price, cost_price):
        return selling_price - cost_price

    @staticmethod
    def calculate_remaining_quantity(initial_quantity, quantity_sold):
        return initial_quantity - quantity_sold

    @staticmethod
    def calculate_remaining_inventory_value(remaining_quantity, cost_price):
        return remaining_quantity * cost_price