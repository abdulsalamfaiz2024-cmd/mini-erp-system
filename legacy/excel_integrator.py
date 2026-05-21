import pandas as pd
import sqlite3
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np


class PerfectExcelIntegration:
    def __init__(self, excel_file_path="كشف البظاعة الحقيقي.xlsx"):
        self.excel_file_path = excel_file_path
        self.db = TailoredDatabase()

        # تحميل البيانات فور الإنشاء
        if os.path.exists(self.excel_file_path):
            self.load_all_data()
        else:
            print(f"الملف غير موجود: {self.excel_file_path}")
            self.create_empty_excel_template()

    def load_all_data(self):
        """تحميل جميع البيانات من جميع الأوراق بربط محكم"""
        try:
            print("جاري تحميل البيانات من جميع الأوراق...")

            # تحميل جميع الأوراق
            self.inventory_df = pd.read_excel(self.excel_file_path, sheet_name='الرئيسية')
            self.invoices_df = pd.read_excel(self.excel_file_path, sheet_name='الفواتير')
            self.sales_df = pd.read_excel(self.excel_file_path, sheet_name='المبيعات')
            self.collections_df = pd.read_excel(self.excel_file_path, sheet_name='التحصيلات')

            print("✓ تم تحميل جميع الأوراق بنجاح")

            # استيراد البيانات بالترتيب الصحيح
            self.import_customers_precise()
            self.import_products_precise()
            self.import_sales_precise()
            self.import_invoices_precise()
            self.import_collections_precise()

            print("✓ تم استيراد جميع البيانات إلى النظام")

        except Exception as e:
            print(f"خطأ في تحميل البيانات: {str(e)}")

    def import_products_precise(self):
        """استيراد المنتجات بدقة من الورقة الرئيسية مع الربط الصحيح لـ Index"""
        print("جاري استيراد المنتجات بدقة...")

        product_count = 0
        for idx, row in self.inventory_df.iterrows():
            # تخطي الصفوف الأولى (العناوين) والصفوف الفارغة
            if idx >= 1 and pd.notna(row.get('Index')) and pd.notna(row.get('اسم الصنف')):
                try:
                    product_index = int(row['Index'])
                    product_id = f"P{product_index:03d}"
                    product_name = row['اسم الصنف']

                    # استخراج الأسعار والكميات مع المعالجة الصحيحة
                    cost_price = self.safe_float_conversion(row.get('السعلر للحبة', 0))
                    selling_price = self.safe_float_conversion(row.get('سعر البيع للحبة', 0))
                    quantity = self.safe_int_conversion(row.get('الكمية', 0))
                    quantity_sold = self.safe_int_conversion(row.get('الكمية المبيوعة', 0))

                    # حساب الكمية المتبقية
                    remaining_quantity = quantity - quantity_sold

                    # إدخال المنتج بجميع التفاصيل
                    self.db.execute_query('''
                        INSERT OR REPLACE INTO products 
                        (product_id, name, cost_price, selling_price, 
                         initial_quantity, quantity_sold, current_stock, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        product_id, product_name, cost_price, selling_price,
                        quantity, quantity_sold, remaining_quantity,
                        row.get('ملاحظات', '') if pd.notna(row.get('ملاحظات')) else ''
                    ))

                    product_count += 1
                    print(f"✓ تم استيراد المنتج: {product_name} (Index: {product_index})")

                except (ValueError, TypeError) as e:
                    print(f"⚠ خطأ في المنتج {row.get('Index')}: {str(e)}")
                    continue

        print(f"✓ تم استيراد {product_count} منتج")

    def import_customers_precise(self):
        """استيراد العملاء بدقة من جميع الأوراق"""
        print("جاري استيراد العملاء...")

        customers_data = []

        # من ورقة المبيعات
        for idx, row in self.sales_df.iterrows():
            if idx >= 0 and pd.notna(row.get('الجهة')) and row['الجهة'] not in ['', ' ']:
                customers_data.append({
                    'name': row['الجهة'],
                    'customer_id': f"S{idx + 1:04d}",
                    'type': 'عميل'
                })

        # من ورقة الفواتير
        for idx, row in self.invoices_df.iterrows():
            if idx >= 0 and pd.notna(row.get('الجهة')) and row['الجهة'] not in ['', ' ']:
                customers_data.append({
                    'name': row['الجهة'],
                    'customer_id': f"I{idx + 1:04d}",
                    'type': 'عميل'
                })

        # من ورقة التحصيلات
        for idx, row in self.collections_df.iterrows():
            if idx >= 0 and pd.notna(row.get('الجهة')) and row['الجهة'] not in ['', ' ']:
                customers_data.append({
                    'name': row['الجهة'],
                    'customer_id': f"COL{idx + 1:04d}",
                    'type': 'عميل'
                })

        # إزالة التكرارات
        unique_customers = []
        seen_names = set()
        for customer in customers_data:
            if customer['name'] not in seen_names:
                unique_customers.append(customer)
                seen_names.add(customer['name'])

        # إدخال في قاعدة البيانات
        for customer in unique_customers:
            self.db.execute_query('''
                INSERT OR REPLACE INTO customers 
                (customer_id, name, customer_type, created_date)
                VALUES (?, ?, ?, ?)
            ''', (customer['customer_id'], customer['name'], customer['type'], datetime.now().strftime('%Y-%m-%d')))

        print(f"✓ تم استيراد {len(unique_customers)} عميل")

    def import_sales_precise(self):
        """استيراد بيانات المبيعات بدقة من ورقة المبيعات"""
        print("جاري استيراد المبيعات...")

        sales_count = 0
        for idx, row in self.sales_df.iterrows():
            # تخطي الصفوف الفارغة
            if idx >= 0 and pd.notna(row.get('رقم الفاتورة')) and row['رقم الفاتورة'] not in ['', ' ']:
                try:
                    invoice_number = f"S{int(row['رقم الفاتورة']):04d}"
                    customer_name = row['الجهة']

                    # الحصول على معرف العميل
                    customer = self.db.fetch_one(
                        "SELECT customer_id FROM customers WHERE name = ?",
                        (customer_name,)
                    )

                    if customer:
                        customer_id = customer[0]

                        # استخراج المبالغ
                        total_amount = self.safe_float_conversion(row.get('اجمالي السعر', 0))
                        paid_amount = self.safe_float_conversion(row.get('المدفوع', 0))
                        remaining_amount = self.safe_float_conversion(row.get('المتبقي', 0))

                        # استخراج التاريخ
                        sale_date = datetime.now().strftime('%Y-%m-%d')
                        if pd.notna(row.get('التاريخ')):
                            try:
                                sale_date = pd.to_datetime(row['التاريخ']).strftime('%Y-%m-%d')
                            except:
                                pass

                        # تحديد حالة الدفع
                        payment_status = 'مدفوعة' if paid_amount >= total_amount else 'جزئية' if paid_amount > 0 else 'غير مدفوعة'

                        # إدخال البيع
                        self.db.execute_query('''
                            INSERT OR REPLACE INTO sales 
                            (invoice_number, customer_id, sale_date, total_amount, 
                             paid_amount, remaining_amount, payment_status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            invoice_number, customer_id, sale_date, total_amount,
                            paid_amount, remaining_amount, payment_status,
                            row.get('ملاحظات', '') if pd.notna(row.get('ملاحظات')) else ''
                        ))

                        sales_count += 1

                except (ValueError, TypeError) as e:
                    print(f"⚠ خطأ في فاتورة المبيعات {row.get('رقم الفاتورة')}: {str(e)}")
                    continue

        print(f"✓ تم استيراد {sales_count} فاتورة مبيعات")

    def import_invoices_precise(self):
        """استيراد تفاصيل الفواتير بدقة من ورقة الفواتير"""
        print("جاري استيراد تفاصيل الفواتير...")

        invoice_count = 0
        for idx, row in self.invoices_df.iterrows():
            if idx >= 0 and pd.notna(row.get('رقم الفاتورة')) and row['رقم الفاتورة'] not in ['', ' ']:
                try:
                    invoice_number = f"INV{int(row['رقم الفاتورة']):04d}"
                    customer_name = row['الجهة']
                    product_index = self.safe_int_conversion(row.get('Index', 0))

                    # الحصول على معرف العميل
                    customer = self.db.fetch_one(
                        "SELECT customer_id FROM customers WHERE name = ?",
                        (customer_name,)
                    )

                    if customer and product_index > 0:
                        customer_id = customer[0]
                        product_id = f"P{product_index:03d}"
                        quantity = self.safe_int_conversion(row.get('الكمية', 0))
                        unit_price = self.safe_float_conversion(row.get('السعر للحبة', 0))
                        total_price = self.safe_float_conversion(row.get('المجموع', 0))

                        # إدخال عنصر الفاتورة
                        self.db.execute_query('''
                            INSERT OR REPLACE INTO invoice_items 
                            (invoice_number, customer_id, product_id, quantity, 
                             unit_price, total_price, line_number)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            invoice_number, customer_id, product_id, quantity,
                            unit_price, total_price, idx
                        ))

                        invoice_count += 1

                except (ValueError, TypeError) as e:
                    print(f"⚠ خطأ في فاتورة {row.get('رقم الفاتورة')}: {str(e)}")
                    continue

        print(f"✓ تم استيراد {invoice_count} عنصر فاتورة")

    def import_collections_precise(self):
        """استيراد بيانات التحصيلات بدقة من ورقة التحصيلات"""
        print("جاري استيراد التحصيلات...")

        collection_count = 0
        for idx, row in self.collections_df.iterrows():
            if idx >= 0 and pd.notna(row.get('المبلغ')) and pd.notna(row.get('الجهة')):
                try:
                    customer_name = row['الجهة']
                    amount = self.safe_float_conversion(row.get('المبلغ', 0))

                    # الحصول على معرف العميل
                    customer = self.db.fetch_one(
                        "SELECT customer_id FROM customers WHERE name = ?",
                        (customer_name,)
                    )

                    if customer:
                        customer_id = customer[0]

                        # استخراج التاريخ
                        collection_date = datetime.now().strftime('%Y-%m-%d')
                        if pd.notna(row.get('التاريخ')):
                            try:
                                collection_date = pd.to_datetime(row['التاريخ']).strftime('%Y-%m-%d')
                            except:
                                pass

                        # إدخال التحصيل
                        self.db.execute_query('''
                            INSERT OR REPLACE INTO collections 
                            (customer_id, collection_date, amount, description)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            customer_id, collection_date, amount,
                            f"تحصيل من {customer_name}"
                        ))

                        collection_count += 1

                except (ValueError, TypeError) as e:
                    print(f"⚠ خطأ في التحصيل: {str(e)}")
                    continue

        print(f"✓ تم استيراد {collection_count} تحصيل")

    def safe_float_conversion(self, value):
        """تحويل آمن إلى رقم عشري مع معالجة الصيغ المختلفة"""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
        try:
            if isinstance(value, str):
                # إزالة الفواصل والمسافات الزائدة
                value = value.replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def safe_int_conversion(self, value):
        """تحويل آمن إلى عدد صحيح مع معالجة الصيغ المختلفة"""
        if pd.isna(value) or value == '' or value is None:
            return 0
        try:
            if isinstance(value, str):
                # إزالة الفواصل والمسافات الزائدة
                value = value.replace(',', '').strip()
            return int(float(value))  # معالجة السلاسل العشرية
        except (ValueError, TypeError):
            return 0

    def create_empty_excel_template(self):
        """إنشاء ملف Excel فارغ بالهيكل المطلوب إذا لزم الأمر"""
        try:
            with pd.ExcelWriter(self.excel_file_path, engine='openpyxl') as writer:
                # إنشاء أوراق فارغة بالهيكل الدقيق
                empty_inventory = pd.DataFrame(columns=[
                    'رقم الفاتورة', 'Index', 'اسم الصنف', 'الكمية', 'السعلر للحبة',
                    'الإجمالي', 'سعر البيع للحبة', 'الكمية المبيوعة', 'المجموع',
                    'تكلفة المبيعات', 'الصافي', 'الكمية المتبقية', 'تكلفة البظاعة المتبقية',
                    'الربح لكل حبة', 'ملاحظات'
                ])
                empty_inventory.to_excel(writer, sheet_name='الرئيسية', index=False)

                empty_invoices = pd.DataFrame(columns=[
                    'رقم الفاتورة', 'رقم التعريفي للجهة', 'الجهة', 'Index',
                    'المنتج', 'الكمية', 'السعر للحبة', 'المجموع', 'إجمالي الفاتورة'
                ])
                empty_invoices.to_excel(writer, sheet_name='الفواتير', index=False)

                empty_sales = pd.DataFrame(columns=[
                    'التاريخ', 'رقم الفاتورة', 'الجهة', 'اجمالي السعر',
                    'المدفوع', 'المتبقي', 'ملاحظات'
                ])
                empty_sales.to_excel(writer, sheet_name='المبيعات', index=False)

                empty_collections = pd.DataFrame(columns=[
                    'التاريخ', 'الجهة', 'المبلغ'
                ])
                empty_collections.to_excel(writer, sheet_name='التحصيلات', index=False)

            print(f"✓ تم إنشاء ملف Excel جديد: {self.excel_file_path}")
        except Exception as e:
            print(f"خطأ في إنشاء الملف: {str(e)}")

    def get_all_products(self):
        """الحصول على جميع المنتجات من قاعدة البيانات"""
        return self.db.fetch_all('''
                                 SELECT product_id, name, cost_price, selling_price, current_stock
                                 FROM products
                                 ORDER BY product_id
                                 ''')

    def get_all_customers(self):
        """الحصول على جميع العملاء من قاعدة البيانات"""
        return self.db.fetch_all('''
                                 SELECT customer_id, name, customer_type
                                 FROM customers
                                 ORDER BY name
                                 ''')

    def check_integration_status(self):
        """فحص حالة التكامل بين النظام وملف Excel"""
        try:
            db_products = len(self.db.fetch_all("SELECT * FROM products"))
            db_customers = len(self.db.fetch_all("SELECT * FROM customers"))
            db_sales = len(self.db.fetch_all("SELECT * FROM sales"))

            print("=== حالة التكامل ===")
            print(f"المنتجات في النظام: {db_products}")
            print(f"العملاء في النظام: {db_customers}")
            print(f"فواتير المبيعات في النظام: {db_sales}")
            print("=====================")

            return {
                'products': db_products,
                'customers': db_customers,
                'sales': db_sales
            }
        except Exception as e:
            print(f"خطأ في فحص حالة التكامل: {str(e)}")
            return None


class TailoredDatabase:
    """قاعدة البيانات المخصصة لهيكل ملف Excel"""

    def __init__(self):
        self.conn = sqlite3.connect('perfect_sales_system.db', check_same_thread=False)
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


# اختبار التكامل
if __name__ == "__main__":
    print("بدء تكامل النظام مع ملف Excel...")
    integrator = PerfectExcelIntegration()

    # فحص حالة التكامل
    status = integrator.check_integration_status()

    # عرض بعض البيانات للتأكد
    products = integrator.get_all_products()
    print(f"\nأول 5 منتجات:")
    for product in products[:5]:
        print(f"  - {product[1]} (ID: {product[0]})")

    customers = integrator.get_all_customers()
    print(f"\nأول 5 عملاء:")
    for customer in customers[:5]:
        print(f"  - {customer[1]} (ID: {customer[0]})")

    print("اكتمل تكامل النظام!")