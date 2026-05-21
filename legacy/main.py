import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from excel_integrator import PerfectExcelIntegration
from database_core import TailoredDatabase
import os
from datetime import datetime
import random


class MainSalesSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة المبيعات والمخزون - النظام المتكامل")
        self.root.geometry("1300x900")
        self.root.configure(bg="#f0f0f0")

        self.db = TailoredDatabase()
        self.excel_integrator = None

        self.setup_styles()
        self.setup_ui()
        self.load_initial_data()

    def setup_styles(self):
        """إعداد الأنماط والألوان للتطبيق"""
        self.colors = {
            "primary": "#007bff",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "light": "#f8f9fa",
            "dark": "#343a40",
            "bg": "#f0f0f0",
            "fg": "#212529",
            "heading": "#004085",
        }

        style = ttk.Style()
        style.theme_use('clam')

        # الأنماط العامة
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"],
                        font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=10)
        style.configure("TLabelframe", background=self.colors["bg"], font=("Arial", 12, "bold"))
        style.configure("TLabelframe.Label", foreground=self.colors["heading"], background=self.colors["bg"])

        # أنماط الأزرار المخصصة
        style.configure("Primary.TButton", background=self.colors["primary"], foreground="white")
        style.map("Primary.TButton", background=[('active', self.colors["info"])])

        style.configure("Secondary.TButton", background=self.colors["secondary"], foreground="white")
        style.map("Secondary.TButton", background=[('active', self.colors["dark"])])

    def setup_ui(self):
        """إعداد واجهة المستخدم الرئيسية مع جميع الوظائف"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # الشريط العلوي
        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(header_frame, text="نظام إدارة المبيعات والمخزون",
                                font=("Arial", 18, "bold"), foreground=self.colors["heading"])
        title_label.pack(side=tk.LEFT, padx=10)

        # قسم التحكم
        control_frame = ttk.LabelFrame(main_frame, text="لوحة التحكم", padding="15")
        control_frame.pack(fill=tk.X, pady=10, padx=5)

        # أزرار التحكم
        ttk.Button(control_frame, text="تحديث البيانات", command=self.update_data,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="عرض التقارير", command=self.show_reports,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="تصدير البيانات", command=self.export_data,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="فحص التكامل", command=self.check_integration,
                   style="Secondary.TButton").pack(side=tk.LEFT, padx=5)

        # قسم الوظائف
        functions_frame = ttk.LabelFrame(main_frame, text="الوظائف الرئيسية", padding="15")
        functions_frame.pack(fill=tk.X, pady=10, padx=5)

        functions_data = [
            ("مبيعات جديدة", self.open_new_sale, self.colors["success"]),
            ("مشتريات جديدة", self.open_new_purchase, self.colors["primary"]),
            ("تحصيل مدفوعات", self.open_collection, self.colors["warning"]),
            ("إضافة مصروف", self.open_expense, self.colors["danger"]),
            ("إدارة العملاء", self.open_customers_management, self.colors["info"]),
            ("إدارة المنتجات", self.open_products_management, self.colors["dark"])
        ]

        for i, (text, command, color) in enumerate(functions_data):
            btn = tk.Button(functions_frame, text=text, command=command, bg=color, fg="white",
                            font=("Arial", 10, "bold"), width=15, height=2, relief="raised", bd=2)
            btn.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        # قسم الإحصائيات
        self.stats_frame = ttk.LabelFrame(main_frame, text="نظرة سريعة", padding="15")
        self.stats_frame.pack(fill=tk.X, pady=10, padx=5)

        # قسم البيانات الرئيسية (التبويبات)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)

        self.create_all_tabs()
        self.populate_tabs()

    def create_all_tabs(self):
        """إنشاء جميع تبويبات النظام"""
        tabs = {
            "العملاء": "customers_tab",
            "المنتجات": "products_tab",
            "المبيعات": "sales_tab",
            "الفواتير": "invoices_tab",
            "التحصيلات": "collections_tab",
            "المصروفات": "expenses_tab",
        }

        for text, tab_name in tabs.items():
            tab = ttk.Frame(self.notebook)
            setattr(self, tab_name, tab)
            self.notebook.add(tab, text=text)

    # ====== الوظائف الرئيسية ======

    def open_new_sale(self):
        """فتح نافذة إضافة مبيعات جديدة"""
        sale_window = tk.Toplevel(self.root)
        sale_window.title("إضافة فاتورة مبيعات جديدة")
        sale_window.geometry("900x700")

        NewSaleWindow(sale_window, self.db, self)

    def open_new_purchase(self):
        """فتح نافذة إضافة مشتريات"""
        purchase_window = tk.Toplevel(self.root)
        purchase_window.title("إضافة فاتورة مشتريات")
        purchase_window.geometry("900x700")

        NewPurchaseWindow(purchase_window, self.db, self)

    def open_collection(self):
        """فتح نافذة تحصيل مدفوعات"""
        collection_window = tk.Toplevel(self.root)
        collection_window.title("تحصيل مدفوعات العملاء")
        collection_window.geometry("600x500")

        CollectionWindow(collection_window, self.db, self)

    def open_expense(self):
        """فتح نافذة إضافة مصروفات"""
        expense_window = tk.Toplevel(self.root)
        expense_window.title("إضافة مصروف جديد")
        expense_window.geometry("600x500")

        ExpenseWindow(expense_window, self.db, self)

    def open_customers_management(self):
        """فتح نافذة إدارة العملاء"""
        customers_window = tk.Toplevel(self.root)
        customers_window.title("إدارة العملاء")
        customers_window.geometry("800x600")

        CustomersManagementWindow(customers_window, self.db, self)

    def open_products_management(self):
        """فتح نافذة إدارة المنتجات"""
        products_window = tk.Toplevel(self.root)
        products_window.title("إدارة المنتجات والمخزون")
        products_window.geometry("900x600")

        ProductsManagementWindow(products_window, self.db, self)

    def load_initial_data(self):
        """تحميل البيانات الأولية من ملف Excel مع التحقق"""
        if os.path.exists("كشف البظاعة الحقيقي.xlsx"):
            try:
                self.excel_integrator = PerfectExcelIntegration()

                # التحقق من التكامل
                status = self.excel_integrator.check_integration_status()

                if status and status['products'] > 0:
                    self.update_quick_stats()
                    self.populate_tabs()
                    messagebox.showinfo("نجاح",
                                        f"تم تحميل البيانات بنجاح!\nالمنتجات: {status['products']}\nالعملاء: {status['customers']}\nفواتير المبيعات: {status['sales']}")
                else:
                    messagebox.showwarning("تحذير", "تم تحميل الملف ولكن لم يتم العثور على بيانات كافية")

            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في تحميل البيانات: {str(e)}")
        else:
            messagebox.showwarning("تحذير", "ملف Excel غير موجود. يرجى التأكد من وجود الملف في نفس المجلد.")

    def update_data(self):
        """تحديث البيانات من ملف Excel"""
        try:
            self.excel_integrator = PerfectExcelIntegration()
            self.update_quick_stats()
            self.populate_tabs()
            messagebox.showinfo("نجاح", "تم تحديث البيانات بنجاح!")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحديث البيانات: {str(e)}")

    def check_integration(self):
        """فحص حالة التكامل بين النظام وملف Excel"""
        try:
            if self.excel_integrator:
                status = self.excel_integrator.check_integration_status()
                if status:
                    messagebox.showinfo("حالة التكامل",
                                        f"المنتجات: {status['products']}\n"
                                        f"العملاء: {status['customers']}\n"
                                        f"فواتير المبيعات: {status['sales']}\n"
                                        f"التكامل: ✓ نشط")
                else:
                    messagebox.showwarning("حالة التكامل", "لم يتم تحميل البيانات بشكل صحيح")
            else:
                messagebox.showwarning("تحذير", "لم يتم تهيئة النظام بعد")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في فحص التكامل: {str(e)}")

    def update_quick_stats(self):
        """تحديث الإحصائيات السريعة بدقة"""
        # مسح الإطار القديم
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        try:
            # الحصول على الإحصائيات الدقيقة
            total_customers = self.db.fetch_one("SELECT COUNT(*) FROM customers")[0] or 0
            total_products = self.db.fetch_one("SELECT COUNT(*) FROM products")[0] or 0
            total_sales = self.db.fetch_one("SELECT COUNT(*) FROM sales")[0] or 0

            sales_amount = self.db.fetch_one("SELECT SUM(total_amount) FROM sales")[0] or 0
            paid_amount = self.db.fetch_one("SELECT SUM(paid_amount) FROM sales")[0] or 0
            remaining_amount = self.db.fetch_one("SELECT SUM(remaining_amount) FROM sales")[0] or 0

            # الحصول على إجمالي المخزون
            total_stock = self.db.fetch_one("SELECT SUM(current_stock) FROM products")[0] or 0
            total_value = self.db.fetch_one("SELECT SUM(current_stock * cost_price) FROM products")[0] or 0

            stats_text = f"""
            العملاء: {total_customers} | المنتجات: {total_products} | المبيعات: {total_sales}
            إجمالي المبيعات: {sales_amount:,.2f} ريال | المدفوع: {paid_amount:,.2f} ريال | المتبقي: {remaining_amount:,.2f} ريال
            المخزون الحالي: {total_stock} وحدة | قيمة المخزون: {total_value:,.2f} ريال
            """

            stats_label = ttk.Label(self.stats_frame, text=stats_text, font=("Arial", 11),
                                    justify=tk.CENTER, foreground="darkgreen")
            stats_label.pack(pady=10)

        except Exception as e:
            print(f"خطأ في تحديث الإحصائيات: {str(e)}")

    def populate_tabs(self):
        """تعبئة جميع التبويبات بالبيانات"""
        self.populate_customers_tab()
        self.populate_products_tab()
        self.populate_sales_tab()
        self.populate_invoices_tab()
        self.populate_collections_tab()
        self.populate_expenses_tab()

    def populate_customers_tab(self):
        """تعبئة تبويب العملاء"""
        for widget in self.customers_tab.winfo_children():
            widget.destroy()

        # إنشاء إطار رئيسي مع شريط التمرير
        main_frame = ttk.Frame(self.customers_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "اسم العميل", "النوع", "تاريخ الإضافة", "الهاتف", "العنوان")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # تحديد العناوين والعروض
        column_widths = {
            "ID": 80,
            "اسم العميل": 200,
            "النوع": 100,
            "تاريخ الإضافة": 120,
            "الهاتف": 120,
            "العنوان": 150
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 120))

        # إضافة أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # جلب بيانات العملاء
        try:
            customers = self.db.fetch_all(
                "SELECT customer_id, name, customer_type, created_date, phone, address FROM customers")
            for customer in customers:
                tree.insert("", tk.END, values=customer)

            print(f"✓ تم تحميل {len(customers)} عميل في التبويب")

        except Exception as e:
            print(f"خطأ في تحميل العملاء: {str(e)}")

        # ترتيب العناصر في الواجهة
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_products_tab(self):
        """تعبئة تبويب المنتجات بجميع البيانات"""
        for widget in self.products_tab.winfo_children():
            widget.destroy()

        # إنشاء إطار رئيسي مع شريط التمرير
        main_frame = ttk.Frame(self.products_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # إنشاء Treeview مع أعمدة إضافية
        columns = ("ID", "Index", "اسم المنتج", "سعر التكلفة", "سعر البيع", "المخزون", "المباع", "الكمية الإجمالية",
                   "الملاحظات")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # تحديد العناوين والعروض
        column_widths = {
            "ID": 80,
            "Index": 60,
            "اسم المنتج": 200,
            "سعر التكلفة": 100,
            "سعر البيع": 100,
            "المخزون": 80,
            "المباع": 80,
            "الكمية الإجمالية": 120,
            "الملاحظات": 150
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 100))

        # إضافة أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # تعبئة البيانات
        try:
            products = self.db.fetch_all('''
                                         SELECT product_id,
                                                name,
                                                cost_price,
                                                selling_price,
                                                current_stock,
                                                quantity_sold,
                                                initial_quantity,
                                                notes
                                         FROM products
                                         ORDER BY CAST(SUBSTR(product_id, 2) AS INTEGER)
                                         ''')

            for product in products:
                # استخراج Index من product_id (مثال: P101 → 101)
                index = product[0][1:] if product[0].startswith('P') else product[0]
                tree.insert("", tk.END, values=(
                    product[0],  # ID
                    index,  # Index
                    product[1],  # Name
                    f"{product[2]:.2f}",  # Cost Price
                    f"{product[3]:.2f}",  # Selling Price
                    product[4],  # Current Stock
                    product[5],  # Quantity Sold
                    product[6],  # Initial Quantity
                    product[7] if product[7] else ""  # Notes
                ))

            print(f"✓ تم تحميل {len(products)} منتج في التبويب")

        except Exception as e:
            print(f"خطأ في تحميل المنتجات: {str(e)}")

        # ترتيب العناصر في الواجهة
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_sales_tab(self):
        """تعبئة تبويب المبيعات"""
        for widget in self.sales_tab.winfo_children():
            widget.destroy()

        # إنشاء إطار رئيسي مع شريط التمرير
        main_frame = ttk.Frame(self.sales_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("رقم الفاتورة", "العميل", "التاريخ", "الإجمالي", "المدفوع", "المتبقي", "الحالة", "الملاحظات")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # تحديد العناوين والعروض
        column_widths = {
            "رقم الفاتورة": 120,
            "العميل": 150,
            "التاريخ": 100,
            "الإجمالي": 100,
            "المدفوع": 100,
            "المتبقي": 100,
            "الحالة": 100,
            "الملاحظات": 150
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 120))

        # إضافة أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # جلب بيانات المبيعات
        try:
            sales = self.db.fetch_all('''
                                      SELECT s.invoice_number,
                                             c.name,
                                             s.sale_date,
                                             s.total_amount,
                                             s.paid_amount,
                                             s.remaining_amount,
                                             s.payment_status,
                                             s.notes
                                      FROM sales s
                                               LEFT JOIN customers c ON s.customer_id = c.customer_id
                                      ORDER BY s.sale_date DESC
                                      ''')

            for sale in sales:
                tree.insert("", tk.END, values=(
                    sale[0],  # Invoice Number
                    sale[1] if sale[1] else "غير محدد",  # Customer Name
                    sale[2],  # Sale Date
                    f"{sale[3]:.2f}",  # Total Amount
                    f"{sale[4]:.2f}",  # Paid Amount
                    f"{sale[5]:.2f}",  # Remaining Amount
                    sale[6],  # Payment Status
                    sale[7] if sale[7] else ""  # Notes
                ))

            print(f"✓ تم تحميل {len(sales)} فاتورة مبيعات في التبويب")

        except Exception as e:
            print(f"خطأ في تحميل المبيعات: {str(e)}")

        # ترتيب العناصر في الواجهة
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_invoices_tab(self):
        """تعبئة تبويب الفواتير"""
        for widget in self.invoices_tab.winfo_children():
            widget.destroy()

        # إنشاء إطار رئيسي مع شريط التمرير
        main_frame = ttk.Frame(self.invoices_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("رقم الفاتورة", "العميل", "المنتج", "الكمية", "سعر الوحدة", "الإجمالي", "رقم البند")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # تحديد العناوين والعروض
        column_widths = {
            "رقم الفاتورة": 120,
            "العميل": 150,
            "المنتج": 200,
            "الكمية": 80,
            "سعر الوحدة": 100,
            "الإجمالي": 100,
            "رقم البند": 80
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 120))

        # إضافة أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # جلب بيانات الفواتير
        try:
            invoices = self.db.fetch_all('''
                                         SELECT i.invoice_number,
                                                c.name,
                                                p.name,
                                                i.quantity,
                                                i.unit_price,
                                                i.total_price,
                                                i.line_number
                                         FROM invoice_items i
                                                  LEFT JOIN customers c ON i.customer_id = c.customer_id
                                                  LEFT JOIN products p ON i.product_id = p.product_id
                                         ORDER BY i.invoice_number, i.line_number
                                         ''')

            for invoice in invoices:
                tree.insert("", tk.END, values=(
                    invoice[0],  # Invoice Number
                    invoice[1] if invoice[1] else "غير محدد",  # Customer Name
                    invoice[2] if invoice[2] else "غير محدد",  # Product Name
                    invoice[3],  # Quantity
                    f"{invoice[4]:.2f}",  # Unit Price
                    f"{invoice[5]:.2f}",  # Total Price
                    invoice[6]  # Line Number
                ))

            print(f"✓ تم تحميل {len(invoices)} عنصر فاتورة في التبويب")

        except Exception as e:
            print(f"خطأ في تحميل الفواتير: {str(e)}")

        # ترتيب العناصر في الواجهة
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_collections_tab(self):
        """تعبئة تبويب التحصيلات"""
        for widget in self.collections_tab.winfo_children():
            widget.destroy()

        # إنشاء إطار رئيسي مع شريط التمرير
        main_frame = ttk.Frame(self.collections_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("التاريخ", "العميل", "المبلغ", "الوصف")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # تحديد العناوين والعروض
        column_widths = {
            "التاريخ": 120,
            "العميل": 200,
            "المبلغ": 100,
            "الوصف": 200
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 150))

        # إضافة أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # جلب بيانات التحصيلات
        try:
            collections = self.db.fetch_all('''
                                            SELECT c.collection_date, cust.name, c.amount, c.description
                                            FROM collections c
                                                     LEFT JOIN customers cust ON c.customer_id = cust.customer_id
                                            ORDER BY c.collection_date DESC
                                            ''')

            for collection in collections:
                tree.insert("", tk.END, values=(
                    collection[0],  # Collection Date
                    collection[1] if collection[1] else "غير محدد",  # Customer Name
                    f"{collection[2]:.2f}",  # Amount
                    collection[3] if collection[3] else ""  # Description
                ))

            print(f"✓ تم تحميل {len(collections)} تحصيل في التبويب")

        except Exception as e:
            print(f"خطأ في تحميل التحصيلات: {str(e)}")

        # ترتيب العناصر في الواجهة
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def populate_expenses_tab(self):
        """تعبئة تبويب المصروفات"""
        for widget in self.expenses_tab.winfo_children():
            widget.destroy()

        # إنشاء إطار رئيسي مع شريط التمرير
        main_frame = ttk.Frame(self.expenses_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "التاريخ", "نوع المصروف", "المبلغ", "الوصف", "الملاحظات")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        # تحديد العناوين والعروض
        column_widths = {
            "ID": 80,
            "التاريخ": 120,
            "نوع المصروف": 150,
            "المبلغ": 100,
            "الوصف": 200,
            "الملاحظات": 150
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=column_widths.get(col, 120))

        # إضافة أشرطة التمرير
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # جلب بيانات المصروفات
        try:
            expenses = self.db.fetch_all('''
                                         SELECT expense_id, expense_date, expense_type, amount, description, notes
                                         FROM expenses
                                         ORDER BY expense_date DESC
                                         ''')

            for expense in expenses:
                tree.insert("", tk.END, values=expense)

            print(f"✓ تم تحميل {len(expenses)} مصروف في التبويب")

        except Exception as e:
            # إذا لم يكن جدول المصروفات موجوداً بعد
            info_label = ttk.Label(main_frame, text="لم يتم إضافة مصروفات بعد",
                                   font=("Arial", 12), foreground="blue")
            info_label.pack(pady=50)

        # ترتيب العناصر في الواجهة
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def show_reports(self):
        """عرض التقارير المتقدمة"""
        reports_window = tk.Toplevel(self.root)
        reports_window.title("التقارير المتقدمة")
        reports_window.geometry("1000x700")

        notebook = ttk.Notebook(reports_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # تقرير المبيعات
        sales_report_frame = ttk.Frame(notebook)
        notebook.add(sales_report_frame, text="تقرير المبيعات")
        self.create_sales_report(sales_report_frame)

        # تقرير العملاء
        customers_report_frame = ttk.Frame(notebook)
        notebook.add(customers_report_frame, text="تقرير العملاء")
        self.create_customers_report(customers_report_frame)

        # تقرير المنتجات
        products_report_frame = ttk.Frame(notebook)
        notebook.add(products_report_frame, text="تقرير المنتجات")
        self.create_products_report(products_report_frame)

        # تقرير المخزون
        inventory_report_frame = ttk.Frame(notebook)
        notebook.add(inventory_report_frame, text="تقرير المخزون")
        self.create_inventory_report(inventory_report_frame)

    def create_sales_report(self, parent_frame):
        """إنشاء تقرير المبيعات"""
        # العنوان
        title_label = ttk.Label(parent_frame, text="تقرير المبيعات الشامل",
                                font=("Arial", 16, "bold"), foreground="darkblue")
        title_label.pack(pady=10)

        # إطار الإحصائيات
        stats_frame = ttk.LabelFrame(parent_frame, text="إحصائيات المبيعات", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        try:
            # إحصائيات المبيعات
            total_sales = self.db.fetch_one("SELECT COUNT(*) FROM sales")[0] or 0
            total_amount = self.db.fetch_one("SELECT SUM(total_amount) FROM sales")[0] or 0
            total_paid = self.db.fetch_one("SELECT SUM(paid_amount) FROM sales")[0] or 0
            total_remaining = self.db.fetch_one("SELECT SUM(remaining_amount) FROM sales")[0] or 0

            stats_text = f"""
            إجمالي الفواتير: {total_sales}
            إجمالي المبيعات: {total_amount:,.2f} ريال
            إجمالي المدفوع: {total_paid:,.2f} ريال
            إجمالي المتبقي: {total_remaining:,.2f} ريال
            """

            stats_label = ttk.Label(stats_frame, text=stats_text, font=("Arial", 11),
                                    justify=tk.LEFT)
            stats_label.pack(pady=5)

        except Exception as e:
            error_label = ttk.Label(stats_frame, text=f"خطأ في تحميل الإحصائيات: {str(e)}",
                                    foreground="red")
            error_label.pack(pady=5)

        # جدول المبيعات التفصيلي
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("رقم الفاتورة", "العميل", "التاريخ", "الإجمالي", "المدفوع", "المتبقي", "الحالة")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # تعبئة البيانات
        try:
            sales = self.db.fetch_all('''
                                      SELECT s.invoice_number,
                                             c.name,
                                             s.sale_date,
                                             s.total_amount,
                                             s.paid_amount,
                                             s.remaining_amount,
                                             s.payment_status
                                      FROM sales s
                                               LEFT JOIN customers c ON s.customer_id = c.customer_id
                                      ORDER BY s.sale_date DESC
                                      ''')

            for sale in sales:
                tree.insert("", tk.END, values=(
                    sale[0], sale[1] or "غير محدد", sale[2],
                    f"{sale[3]:.2f}", f"{sale[4]:.2f}", f"{sale[5]:.2f}", sale[6]
                ))

        except Exception as e:
            print(f"خطأ في تحميل تقرير المبيعات: {str(e)}")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_customers_report(self, parent_frame):
        """إنشاء تقرير العملاء"""
        title_label = ttk.Label(parent_frame, text="تقرير العملاء",
                                font=("Arial", 16, "bold"), foreground="darkblue")
        title_label.pack(pady=10)

        # إحصائيات العملاء
        stats_frame = ttk.LabelFrame(parent_frame, text="إحصائيات العملاء", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        try:
            total_customers = self.db.fetch_one("SELECT COUNT(*) FROM customers")[0] or 0
            total_debt = self.db.fetch_one("SELECT SUM(remaining_amount) FROM sales")[0] or 0

            stats_text = f"""
            إجمالي العملاء: {total_customers}
            إجمالي الديون: {total_debt:,.2f} ريال
            """

            stats_label = ttk.Label(stats_frame, text=stats_text, font=("Arial", 11))
            stats_label.pack(pady=5)

        except Exception as e:
            error_label = ttk.Label(stats_frame, text=f"خطأ في تحميل الإحصائيات: {str(e)}",
                                    foreground="red")
            error_label.pack(pady=5)

        # جدول العملاء
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("اسم العميل", "عدد الفواتير", "إجمالي المشتريات", "المدفوع", "المتبقي")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # تعبئة البيانات
        try:
            customers_report = self.db.fetch_all('''
                                                 SELECT c.name,
                                                        COUNT(s.sale_id)                     as invoice_count,
                                                        COALESCE(SUM(s.total_amount), 0)     as total_purchases,
                                                        COALESCE(SUM(s.paid_amount), 0)      as total_paid,
                                                        COALESCE(SUM(s.remaining_amount), 0) as total_remaining
                                                 FROM customers c
                                                          LEFT JOIN sales s ON c.customer_id = s.customer_id
                                                 GROUP BY c.customer_id, c.name
                                                 ORDER BY total_purchases DESC
                                                 ''')

            for customer in customers_report:
                tree.insert("", tk.END, values=(
                    customer[0] or "غير محدد",
                    customer[1],
                    f"{customer[2]:.2f}",
                    f"{customer[3]:.2f}",
                    f"{customer[4]:.2f}"
                ))

        except Exception as e:
            print(f"خطأ في تحميل تقرير العملاء: {str(e)}")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_products_report(self, parent_frame):
        """إنشاء تقرير المنتجات"""
        title_label = ttk.Label(parent_frame, text="تقرير المنتجات",
                                font=("Arial", 16, "bold"), foreground="darkblue")
        title_label.pack(pady=10)

        # جدول المنتجات
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("اسم المنتج", "المباع", "الإيرادات", "التكلفة", "الربح")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # تعبئة البيانات
        try:
            products_report = self.db.fetch_all('''
                                                SELECT p.name,
                                                       p.quantity_sold,
                                                       (p.quantity_sold * p.selling_price)                  as revenue,
                                                       (p.quantity_sold * p.cost_price)                     as cost,
                                                       (p.quantity_sold * (p.selling_price - p.cost_price)) as profit
                                                FROM products p
                                                WHERE p.quantity_sold > 0
                                                ORDER BY profit DESC
                                                ''')

            for product in products_report:
                tree.insert("", tk.END, values=(
                    product[0],
                    product[1],
                    f"{product[2]:.2f}",
                    f"{product[3]:.2f}",
                    f"{product[4]:.2f}"
                ))

        except Exception as e:
            print(f"خطأ في تحميل تقرير المنتجات: {str(e)}")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_inventory_report(self, parent_frame):
        """إنشاء تقرير المخزون"""
        title_label = ttk.Label(parent_frame, text="تقرير المخزون",
                                font=("Arial", 16, "bold"), foreground="darkblue")
        title_label.pack(pady=10)

        # إحصائيات المخزون
        stats_frame = ttk.LabelFrame(parent_frame, text="إحصائيات المخزون", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        try:
            total_products = self.db.fetch_one("SELECT COUNT(*) FROM products")[0] or 0
            total_stock = self.db.fetch_one("SELECT SUM(current_stock) FROM products")[0] or 0
            total_value = self.db.fetch_one("SELECT SUM(current_stock * cost_price) FROM products")[0] or 0
            out_of_stock = self.db.fetch_one("SELECT COUNT(*) FROM products WHERE current_stock = 0")[0] or 0

            stats_text = f"""
            إجمالي المنتجات: {total_products}
            إجمالي المخزون: {total_stock} وحدة
            قيمة المخزون: {total_value:,.2f} ريال
            المنتجات المنتهية: {out_of_stock}
            """

            stats_label = ttk.Label(stats_frame, text=stats_text, font=("Arial", 11))
            stats_label.pack(pady=5)

        except Exception as e:
            error_label = ttk.Label(stats_frame, text=f"خطأ في تحميل الإحصائيات: {str(e)}",
                                    foreground="red")
            error_label.pack(pady=5)

        # جدول المخزون
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("اسم المنتج", "المخزون", "سعر التكلفة", "قيمة المخزون", "الحالة")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # تعبئة البيانات
        try:
            inventory = self.db.fetch_all('''
                                          SELECT name,
                                                 current_stock,
                                                 cost_price,
                                                 (current_stock * cost_price) as stock_value
                                          FROM products
                                          ORDER BY current_stock ASC, stock_value DESC
                                          ''')

            for item in inventory:
                status = "منتهي" if item[1] == 0 else "منخفض" if item[1] < 10 else "جيد"
                status_color = "red" if item[1] == 0 else "orange" if item[1] < 10 else "green"

                tree.insert("", tk.END, values=(
                    item[0],
                    item[1],
                    f"{item[2]:.2f}",
                    f"{item[3]:.2f}",
                    status
                ))

        except Exception as e:
            print(f"خطأ في تحميل تقرير المخزون: {str(e)}")

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def export_data(self):
        """تصدير البيانات إلى Excel"""
        try:
            from excel_integrator import PerfectExcelIntegration

            # اختيار مكان الحفظ
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="حفظ التقرير كملف Excel"
            )

            if file_path:
                # إنشاء ملف Excel جديد
                integrator = PerfectExcelIntegration()

                # تصدير البيانات
                integrator.export_to_excel(file_path)
                messagebox.showinfo("نجاح", f"تم تصدير البيانات بنجاح إلى:\n{file_path}")

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في التصدير: {str(e)}")


# ====== نافذة المبيعات ======

class NewSaleWindow:
    def __init__(self, root, db, parent_system):
        self.root = root
        self.db = db
        self.parent_system = parent_system
        self.sale_items = []

        self.setup_ui()
        self.generate_invoice_number()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # عنوان النافذة
        title_label = ttk.Label(main_frame, text="إضافة فاتورة مبيعات جديدة",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # معلومات الفاتورة
        info_frame = ttk.LabelFrame(main_frame, text="معلومات الفاتورة", padding="10")
        info_frame.pack(fill=tk.X, pady=10)

        # رقم الفاتورة
        ttk.Label(info_frame, text="رقم الفاتورة:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.invoice_entry = ttk.Entry(info_frame, width=20, state='readonly')
        self.invoice_entry.grid(row=0, column=1, padx=5, pady=5)

        # العميل
        ttk.Label(info_frame, text="العميل:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.customer_combo = ttk.Combobox(info_frame, width=20)
        self.customer_combo.grid(row=0, column=3, padx=5, pady=5)
        self.load_customers()

        # التاريخ
        ttk.Label(info_frame, text="التاريخ:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(info_frame, width=20)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        # إضافة المنتجات
        product_frame = ttk.LabelFrame(main_frame, text="إضافة منتجات", padding="10")
        product_frame.pack(fill=tk.X, pady=10)

        # حقول إدخال المنتج
        ttk.Label(product_frame, text="المنتج:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_combo = ttk.Combobox(product_frame, width=20)
        self.product_combo.grid(row=0, column=1, padx=5, pady=5)
        self.product_combo.bind('<<ComboboxSelected>>', self.on_product_selected)
        self.load_products()

        ttk.Label(product_frame, text="الكمية:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(product_frame, width=15)
        self.quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(product_frame, text="سعر البيع:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.price_entry = ttk.Entry(product_frame, width=15)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(product_frame, text="المخزون المتاح:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.stock_label = ttk.Label(product_frame, text="0", foreground="blue")
        self.stock_label.grid(row=1, column=3, padx=5, pady=5)

        # أزرار التحكم
        button_frame = ttk.Frame(product_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="إضافة المنتج", command=self.add_product_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="مسح الحقول", command=self.clear_product_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="إزالة المحدد", command=self.remove_selected_item).pack(side=tk.LEFT, padx=5)

        # جدول المنتجات المضافة
        table_frame = ttk.LabelFrame(main_frame, text="المنتجات المضافة", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("المنتج", "الكمية", "سعر الوحدة", "الإجمالي")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الإجمالي وحفظ الفاتورة
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)

        self.total_label = ttk.Label(bottom_frame, text="الإجمالي: 0.00 ريال", font=("Arial", 12, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=20)

        ttk.Button(bottom_frame, text="حفظ الفاتورة", command=self.save_sale).pack(side=tk.RIGHT, padx=20)
        ttk.Button(bottom_frame, text="إلغاء", command=self.root.destroy).pack(side=tk.RIGHT, padx=10)

    def generate_invoice_number(self):
        """توليد رقم فاتورة تلقائي"""
        invoice_num = f"SALE-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        self.invoice_entry.config(state='normal')
        self.invoice_entry.delete(0, tk.END)
        self.invoice_entry.insert(0, invoice_num)
        self.invoice_entry.config(state='readonly')

    def load_customers(self):
        """تحميل قائمة العملاء"""
        try:
            customers = self.db.fetch_all("SELECT name FROM customers")
            customer_names = [customer[0] for customer in customers]
            self.customer_combo['values'] = customer_names
            if customer_names:
                self.customer_combo.set(customer_names[0])
        except Exception as e:
            print(f"خطأ في تحميل العملاء: {str(e)}")

    def load_products(self):
        """تحميل قائمة المنتجات"""
        try:
            products = self.db.fetch_all("SELECT name FROM products WHERE current_stock > 0")
            product_names = [product[0] for product in products]
            self.product_combo['values'] = product_names
            if product_names:
                self.product_combo.set(product_names[0])
                self.on_product_selected(None)
        except Exception as e:
            print(f"خطأ في تحميل المنتجات: {str(e)}")

    def on_product_selected(self, event):
        """عند اختيار منتج"""
        product_name = self.product_combo.get()
        if product_name:
            try:
                product = self.db.fetch_one(
                    "SELECT selling_price, current_stock FROM products WHERE name = ?",
                    (product_name,)
                )
                if product:
                    self.price_entry.delete(0, tk.END)
                    self.price_entry.insert(0, f"{product[0]:.2f}")
                    self.stock_label.config(text=str(product[1]))
            except Exception as e:
                print(f"خطأ في اختيار المنتج: {str(e)}")

    def add_product_item(self):
        """إضافة منتج إلى الفاتورة"""
        try:
            product_name = self.product_combo.get()
            quantity = int(self.quantity_entry.get())
            unit_price = float(self.price_entry.get())

            if not product_name or quantity <= 0:
                messagebox.showerror("خطأ", "يرجى إدخال بيانات المنتج بشكل صحيح")
                return

            # التحقق من المخزون المتاح
            product = self.db.fetch_one(
                "SELECT current_stock FROM products WHERE name = ?",
                (product_name,)
            )
            if product and quantity > product[0]:
                messagebox.showerror("خطأ", f"الكمية المطلوبة ({quantity}) تتجاوز المخزون المتاح ({product[0]})")
                return

            total_price = quantity * unit_price

            # إضافة إلى القائمة
            item = {
                'product_name': product_name,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            }
            self.sale_items.append(item)

            # إضافة إلى الجدول
            self.products_tree.insert("", tk.END, values=(
                product_name, quantity, f"{unit_price:.2f}", f"{total_price:.2f}"
            ))

            self.update_total()
            self.clear_product_fields()

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في الكمية والسعر")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة المنتج: {str(e)}")

    def remove_selected_item(self):
        """إزالة العنصر المحدد من الفاتورة"""
        try:
            selected_item = self.products_tree.selection()
            if selected_item:
                item_index = self.products_tree.index(selected_item[0])
                self.sale_items.pop(item_index)
                self.products_tree.delete(selected_item)
                self.update_total()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إزالة العنصر: {str(e)}")

    def clear_product_fields(self):
        """مسح حقول إدخال المنتج"""
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.stock_label.config(text="0")

    def update_total(self):
        """تحديث الإجمالي"""
        total = sum(item['total_price'] for item in self.sale_items)
        self.total_label.config(text=f"الإجمالي: {total:,.2f} ريال")

    def save_sale(self):
        """حفظ فاتورة المبيعات"""
        if not self.sale_items:
            messagebox.showerror("خطأ", "يرجى إضافة منتجات على الأقل")
            return

        customer_name = self.customer_combo.get()
        if not customer_name:
            messagebox.showerror("خطأ", "يرجى اختيار عميل")
            return

        try:
            # الحصول على معرف العميل
            customer = self.db.fetch_one("SELECT customer_id FROM customers WHERE name = ?", (customer_name,))
            if not customer:
                messagebox.showerror("خطأ", "العميل غير موجود")
                return

            customer_id = customer[0]
            total_amount = sum(item['total_price'] for item in self.sale_items)
            sale_date = self.date_entry.get()
            invoice_number = self.invoice_entry.get()

            # حفظ البيع
            self.db.execute_query('''
                                  INSERT INTO sales (invoice_number, customer_id, sale_date, total_amount, paid_amount,
                                                     remaining_amount, payment_status)
                                  VALUES (?, ?, ?, ?, ?, ?, ?)
                                  ''',
                                  (invoice_number, customer_id, sale_date, total_amount, 0, total_amount, 'غير مدفوعة'))

            # حفظ عناصر الفاتورة وتحديث المخزون
            for i, item in enumerate(self.sale_items):
                product_name = item['product_name']
                quantity_sold = item['quantity']
                unit_price = item['unit_price']
                total_price = item['total_price']

                # الحصول على معرف المنتج
                product = self.db.fetch_one("SELECT product_id FROM products WHERE name = ?", (product_name,))
                if product:
                    product_id = product[0]

                    # إدخال عنصر الفاتورة
                    self.db.execute_query('''
                                          INSERT INTO invoice_items (invoice_number, customer_id, product_id, quantity,
                                                                     unit_price, total_price, line_number)
                                          VALUES (?, ?, ?, ?, ?, ?, ?)
                                          ''', (invoice_number, customer_id, product_id, quantity_sold, unit_price,
                                                total_price, i))

                    # تحديث كمية المنتج المباعة والمخزون
                    self.db.execute_query('''
                                          UPDATE products
                                          SET quantity_sold = quantity_sold + ?,
                                              current_stock = current_stock - ?
                                          WHERE product_id = ?
                                          ''', (quantity_sold, quantity_sold, product_id))

            messagebox.showinfo("نجاح",
                                f"تم حفظ فاتورة المبيعات بنجاح!\nرقم الفاتورة: {invoice_number}\nالمبلغ: {total_amount:,.2f} ريال")
            self.parent_system.update_quick_stats()
            self.parent_system.populate_tabs()
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ الفاتورة: {str(e)}")


# ====== نافذة المشتريات ======

class NewPurchaseWindow:
    def __init__(self, root, db, parent_system):
        self.root = root
        self.db = db
        self.parent_system = parent_system
        self.purchase_items = []

        self.setup_ui()
        self.generate_invoice_number()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="إضافة فاتورة مشتريات",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # معلومات الفاتورة
        info_frame = ttk.LabelFrame(main_frame, text="معلومات الفاتورة", padding="10")
        info_frame.pack(fill=tk.X, pady=10)

        # رقم الفاتورة
        ttk.Label(info_frame, text="رقم الفاتورة:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.invoice_entry = ttk.Entry(info_frame, width=20, state='readonly')
        self.invoice_entry.grid(row=0, column=1, padx=5, pady=5)

        # المورد
        ttk.Label(info_frame, text="المورد:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.supplier_entry = ttk.Entry(info_frame, width=20)
        self.supplier_entry.grid(row=0, column=3, padx=5, pady=5)

        # التاريخ
        ttk.Label(info_frame, text="التاريخ:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(info_frame, width=20)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        # إضافة المنتجات
        product_frame = ttk.LabelFrame(main_frame, text="إضافة منتجات للمشتريات", padding="10")
        product_frame.pack(fill=tk.X, pady=10)

        # حقول إدخال المنتج
        ttk.Label(product_frame, text="اسم المنتج:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.product_entry = ttk.Entry(product_frame, width=20)
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(product_frame, text="الكمية:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(product_frame, width=15)
        self.quantity_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(product_frame, text="سعر التكلفة:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cost_entry = ttk.Entry(product_frame, width=15)
        self.cost_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(product_frame, text="سعر البيع:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.price_entry = ttk.Entry(product_frame, width=15)
        self.price_entry.grid(row=1, column=3, padx=5, pady=5)

        # أزرار التحكم
        button_frame = ttk.Frame(product_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="إضافة المنتج", command=self.add_product_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="مسح الحقول", command=self.clear_product_fields).pack(side=tk.LEFT, padx=5)

        # جدول المنتجات المضافة
        table_frame = ttk.LabelFrame(main_frame, text="المنتجات المضافة", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("اسم المنتج", "الكمية", "سعر التكلفة", "سعر البيع", "الإجمالي")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # الإجمالي وحفظ الفاتورة
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)

        self.total_label = ttk.Label(bottom_frame, text="الإجمالي: 0.00 ريال", font=("Arial", 12, "bold"))
        self.total_label.pack(side=tk.LEFT, padx=20)

        ttk.Button(bottom_frame, text="حفظ فاتورة المشتريات", command=self.save_purchase).pack(side=tk.RIGHT, padx=20)
        ttk.Button(bottom_frame, text="إلغاء", command=self.root.destroy).pack(side=tk.RIGHT, padx=10)

    def generate_invoice_number(self):
        """توليد رقم فاتورة تلقائي"""
        invoice_num = f"PUR-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        self.invoice_entry.config(state='normal')
        self.invoice_entry.delete(0, tk.END)
        self.invoice_entry.insert(0, invoice_num)
        self.invoice_entry.config(state='readonly')

    def add_product_item(self):
        """إضافة منتج إلى فاتورة المشتريات"""
        try:
            product_name = self.product_entry.get()
            quantity = int(self.quantity_entry.get())
            cost_price = float(self.cost_entry.get())
            selling_price = float(self.price_entry.get())

            if not product_name or quantity <= 0:
                messagebox.showerror("خطأ", "يرجى إدخال بيانات المنتج بشكل صحيح")
                return

            total_cost = quantity * cost_price

            # إضافة إلى القائمة
            item = {
                'product_name': product_name,
                'quantity': quantity,
                'cost_price': cost_price,
                'selling_price': selling_price,
                'total_cost': total_cost
            }
            self.purchase_items.append(item)

            # إضافة إلى الجدول
            self.products_tree.insert("", tk.END, values=(
                product_name, quantity, f"{cost_price:.2f}", f"{selling_price:.2f}", f"{total_cost:.2f}"
            ))

            self.update_total()
            self.clear_product_fields()

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في الكمية والأسعار")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة المنتج: {str(e)}")

    def clear_product_fields(self):
        """مسح حقول إدخال المنتج"""
        self.product_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def update_total(self):
        """تحديث الإجمالي"""
        total = sum(item['total_cost'] for item in self.purchase_items)
        self.total_label.config(text=f"الإجمالي: {total:,.2f} ريال")

    def save_purchase(self):
        """حفظ فاتورة المشتريات"""
        if not self.purchase_items:
            messagebox.showerror("خطأ", "يرجى إضافة منتجات على الأقل")
            return

        supplier_name = self.supplier_entry.get()
        if not supplier_name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المورد")
            return

        try:
            total_amount = sum(item['total_cost'] for item in self.purchase_items)
            purchase_date = self.date_entry.get()
            invoice_number = self.invoice_entry.get()

            # إضافة المنتجات الجديدة أو تحديث المخزون
            for item in self.purchase_items:
                product_name = item['product_name']
                quantity = item['quantity']
                cost_price = item['cost_price']
                selling_price = item['selling_price']

                # التحقق إذا كان المنتج موجوداً
                existing_product = self.db.fetch_one("SELECT product_id FROM products WHERE name = ?", (product_name,))

                if existing_product:
                    # تحديث المنتج الموجود
                    product_id = existing_product[0]
                    self.db.execute_query('''
                                          UPDATE products
                                          SET cost_price       = ?,
                                              selling_price    = ?,
                                              initial_quantity = initial_quantity + ?,
                                              current_stock    = current_stock + ?,
                                              last_updated     = ?
                                          WHERE product_id = ?
                                          ''', (cost_price, selling_price, quantity, quantity,
                                                datetime.now().strftime('%Y-%m-%d'), product_id))
                else:
                    # إضافة منتج جديد
                    # إنشاء معرف منتج جديد
                    max_index = self.db.fetch_one("SELECT MAX(CAST(SUBSTR(product_id, 2) AS INTEGER)) FROM products")[
                                    0] or 100
                    new_index = max_index + 1
                    product_id = f"P{new_index:03d}"

                    self.db.execute_query('''
                                          INSERT INTO products
                                          (product_id, name, cost_price, selling_price, initial_quantity, current_stock,
                                           last_updated)
                                          VALUES (?, ?, ?, ?, ?, ?, ?)
                                          ''', (product_id, product_name, cost_price, selling_price, quantity, quantity,
                                                datetime.now().strftime('%Y-%m-%d')))

            messagebox.showinfo("نجاح",
                                f"تم حفظ فاتورة المشتريات بنجاح!\nرقم الفاتورة: {invoice_number}\nالمبلغ: {total_amount:,.2f} ريال")
            self.parent_system.update_quick_stats()
            self.parent_system.populate_tabs()
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ فاتورة المشتريات: {str(e)}")


# ====== نافذة التحصيلات ======

class CollectionWindow:
    def __init__(self, root, db, parent_system):
        self.root = root
        self.db = db
        self.parent_system = parent_system

        self.setup_ui()
        self.load_customers_with_balance()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="تحصيل مدفوعات العملاء",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # معلومات التحصيل
        info_frame = ttk.LabelFrame(main_frame, text="معلومات التحصيل", padding="10")
        info_frame.pack(fill=tk.X, pady=10)

        # العميل
        ttk.Label(info_frame, text="العميل:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.customer_combo = ttk.Combobox(info_frame, width=20)
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5)
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_selected)

        # الرصيد المستحق
        ttk.Label(info_frame, text="الرصيد المستحق:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.balance_label = ttk.Label(info_frame, text="0.00 ريال", foreground="red", font=("Arial", 10, "bold"))
        self.balance_label.grid(row=0, column=3, padx=5, pady=5)

        # المبلغ
        ttk.Label(info_frame, text="المبلغ المحصل:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = ttk.Entry(info_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        # التاريخ
        ttk.Label(info_frame, text="تاريخ التحصيل:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(info_frame, width=20)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=3, padx=5, pady=5)

        # الوصف
        ttk.Label(info_frame, text="وصف التحصيل:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_entry = ttk.Entry(info_frame, width=20)
        self.description_entry.grid(row=2, column=1, padx=5, pady=5)

        # أزرار التحكم
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="حفظ التحصيل", command=self.save_collection).pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_frame, text="إلغاء", command=self.root.destroy).pack(side=tk.RIGHT, padx=10)

        # جدول الفواتير المستحقة
        table_frame = ttk.LabelFrame(main_frame, text="الفواتير المستحقة للعميل", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("رقم الفاتورة", "التاريخ", "الإجمالي", "المدفوع", "المتبقي", "الحالة")
        self.invoices_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.invoices_tree.heading(col, text=col)
            self.invoices_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.invoices_tree.yview)
        self.invoices_tree.configure(yscrollcommand=scrollbar.set)

        self.invoices_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_customers_with_balance(self):
        """تحميل العملاء الذين لديهم رصيد مستحق"""
        try:
            customers = self.db.fetch_all('''
                                          SELECT DISTINCT c.name
                                          FROM customers c
                                                   JOIN sales s ON c.customer_id = s.customer_id
                                          WHERE s.remaining_amount > 0
                                          ORDER BY c.name
                                          ''')
            customer_names = [customer[0] for customer in customers]
            self.customer_combo['values'] = customer_names
        except Exception as e:
            print(f"خطأ في تحميل العملاء: {str(e)}")

    def on_customer_selected(self, event):
        """عند اختيار عميل"""
        customer_name = self.customer_combo.get()
        if customer_name:
            try:
                # حساب الرصيد المستحق
                balance = self.db.fetch_one('''
                                            SELECT SUM(remaining_amount)
                                            FROM sales s
                                                     JOIN customers c ON s.customer_id = c.customer_id
                                            WHERE c.name = ?
                                              AND s.remaining_amount > 0
                                            ''', (customer_name,))

                if balance and balance[0]:
                    self.balance_label.config(text=f"{balance[0]:,.2f} ريال")
                else:
                    self.balance_label.config(text="0.00 ريال")

                # تحميل الفواتير المستحقة
                self.load_customer_invoices(customer_name)

            except Exception as e:
                print(f"خطأ في تحميل بيانات العميل: {str(e)}")

    def load_customer_invoices(self, customer_name):
        """تحميل الفواتير المستحقة للعميل"""
        try:
            # مسح الجدول الحالي
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)

            invoices = self.db.fetch_all('''
                                         SELECT s.invoice_number,
                                                s.sale_date,
                                                s.total_amount,
                                                s.paid_amount,
                                                s.remaining_amount,
                                                s.payment_status
                                         FROM sales s
                                                  JOIN customers c ON s.customer_id = c.customer_id
                                         WHERE c.name = ?
                                           AND s.remaining_amount > 0
                                         ORDER BY s.sale_date
                                         ''', (customer_name,))

            for invoice in invoices:
                self.invoices_tree.insert("", tk.END, values=(
                    invoice[0], invoice[1], f"{invoice[2]:.2f}",
                    f"{invoice[3]:.2f}", f"{invoice[4]:.2f}", invoice[5]
                ))

        except Exception as e:
            print(f"خطأ في تحميل فواتير العميل: {str(e)}")

    def save_collection(self):
        """حفظ عملية التحصيل"""
        customer_name = self.customer_combo.get()
        amount_str = self.amount_entry.get()
        collection_date = self.date_entry.get()
        description = self.description_entry.get()

        if not customer_name:
            messagebox.showerror("خطأ", "يرجى اختيار عميل")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
                return

            # الحصول على معرف العميل
            customer = self.db.fetch_one("SELECT customer_id FROM customers WHERE name = ?", (customer_name,))
            if not customer:
                messagebox.showerror("خطأ", "العميل غير موجود")
                return

            customer_id = customer[0]

            # حفظ التحصيل
            self.db.execute_query('''
                                  INSERT INTO collections (customer_id, collection_date, amount, description)
                                  VALUES (?, ?, ?, ?)
                                  ''', (customer_id, collection_date, amount, description))

            # تحديث رصيد الفواتير (تطبيق المبلغ على الفواتير الأقدم أولاً)
            remaining_amount = amount
            invoices = self.db.fetch_all('''
                                         SELECT invoice_number, remaining_amount
                                         FROM sales
                                         WHERE customer_id = ?
                                           AND remaining_amount > 0
                                         ORDER BY sale_date
                                         ''', (customer_id,))

            for invoice in invoices:
                if remaining_amount <= 0:
                    break

                invoice_number = invoice[0]
                invoice_remaining = invoice[1]

                amount_to_apply = min(remaining_amount, invoice_remaining)

                # تحديث الفاتورة
                self.db.execute_query('''
                                      UPDATE sales
                                      SET paid_amount      = paid_amount + ?,
                                          remaining_amount = remaining_amount - ?,
                                          payment_status   = CASE
                                                                 WHEN (remaining_amount - ?) <= 0 THEN 'مدفوعة'
                                                                 ELSE 'جزئية'
                                              END
                                      WHERE invoice_number = ?
                                      ''', (amount_to_apply, amount_to_apply, amount_to_apply, invoice_number))

                remaining_amount -= amount_to_apply

            messagebox.showinfo("نجاح", f"تم حفظ التحصيل بنجاح!\nالمبلغ: {amount:,.2f} ريال")
            self.parent_system.update_quick_stats()
            self.parent_system.populate_tabs()
            self.root.destroy()

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ التحصيل: {str(e)}")


# ====== نافذة المصروفات ======

class ExpenseWindow:
    def __init__(self, root, db, parent_system):
        self.root = root
        self.db = db
        self.parent_system = parent_system

        self.setup_ui()
        self.create_expenses_table()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="إضافة مصروف جديد",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # معلومات المصروف
        info_frame = ttk.LabelFrame(main_frame, text="معلومات المصروف", padding="10")
        info_frame.pack(fill=tk.X, pady=10)

        # نوع المصروف
        ttk.Label(info_frame, text="نوع المصروف:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.expense_type_combo = ttk.Combobox(info_frame, width=20, values=[
            "رواتب", "إيجار", "كهرباء", "ماء", "اتصالات", "نقل", "مواد مكتبية", "صيانة", "أخرى"
        ])
        self.expense_type_combo.grid(row=0, column=1, padx=5, pady=5)
        self.expense_type_combo.set("أخرى")

        # المبلغ
        ttk.Label(info_frame, text="المبلغ:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.amount_entry = ttk.Entry(info_frame, width=20)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)

        # التاريخ
        ttk.Label(info_frame, text="تاريخ المصروف:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(info_frame, width=20)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)

        # الوصف
        ttk.Label(info_frame, text="وصف المصروف:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.description_entry = ttk.Entry(info_frame, width=20)
        self.description_entry.grid(row=1, column=3, padx=5, pady=5)

        # الملاحظات
        ttk.Label(info_frame, text="ملاحظات:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.notes_entry = ttk.Entry(info_frame, width=20)
        self.notes_entry.grid(row=2, column=1, padx=5, pady=5)

        # أزرار التحكم
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="حفظ المصروف", command=self.save_expense).pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_frame, text="إلغاء", command=self.root.destroy).pack(side=tk.RIGHT, padx=10)

        # جدول المصروفات السابقة
        table_frame = ttk.LabelFrame(main_frame, text="المصروفات السابقة", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("التاريخ", "نوع المصروف", "المبلغ", "الوصف", "الملاحظات")
        self.expenses_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.expenses_tree.heading(col, text=col)
            self.expenses_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)

        self.expenses_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # تحميل المصروفات السابقة
        self.load_previous_expenses()

    def create_expenses_table(self):
        """إنشاء جدول المصروفات إذا لم يكن موجوداً"""
        try:
            self.db.execute_query('''
                                  CREATE TABLE IF NOT EXISTS expenses
                                  (
                                      expense_id
                                      INTEGER
                                      PRIMARY
                                      KEY
                                      AUTOINCREMENT,
                                      expense_date
                                      DATE,
                                      expense_type
                                      TEXT,
                                      amount
                                      REAL
                                      DEFAULT
                                      0,
                                      description
                                      TEXT,
                                      notes
                                      TEXT,
                                      created_date
                                      TIMESTAMP
                                      DEFAULT
                                      CURRENT_TIMESTAMP
                                  )
                                  ''')
        except Exception as e:
            print(f"خطأ في إنشاء جدول المصروفات: {str(e)}")

    def load_previous_expenses(self):
        """تحميل المصروفات السابقة"""
        try:
            expenses = self.db.fetch_all('''
                                         SELECT expense_date, expense_type, amount, description, notes
                                         FROM expenses
                                         ORDER BY expense_date DESC LIMIT 50
                                         ''')

            for expense in expenses:
                self.expenses_tree.insert("", tk.END, values=(
                    expense[0], expense[1], f"{expense[2]:.2f}",
                    expense[3] or "", expense[4] or ""
                ))

        except Exception as e:
            print(f"خطأ في تحميل المصروفات: {str(e)}")

    def save_expense(self):
        """حفظ المصروف"""
        expense_type = self.expense_type_combo.get()
        amount_str = self.amount_entry.get()
        expense_date = self.date_entry.get()
        description = self.description_entry.get()
        notes = self.notes_entry.get()

        if not expense_type or not amount_str:
            messagebox.showerror("خطأ", "يرجى إدخال نوع المصروف والمبلغ")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
                return

            # حفظ المصروف
            self.db.execute_query('''
                                  INSERT INTO expenses (expense_date, expense_type, amount, description, notes)
                                  VALUES (?, ?, ?, ?, ?)
                                  ''', (expense_date, expense_type, amount, description, notes))

            messagebox.showinfo("نجاح", f"تم حفظ المصروف بنجاح!\nالمبلغ: {amount:,.2f} ريال")
            self.parent_system.populate_tabs()
            self.root.destroy()

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال مبلغ صحيح")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ المصروف: {str(e)}")


# ====== نوافذ الإدارة ======

class CustomersManagementWindow:
    def __init__(self, root, db, parent_system):
        self.root = root
        self.db = db
        self.parent_system = parent_system

        self.setup_ui()
        self.load_customers()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="إدارة العملاء",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # إطار الإضافة/التعديل
        form_frame = ttk.LabelFrame(main_frame, text="بيانات العميل", padding="10")
        form_frame.pack(fill=tk.X, pady=10)

        # اسم العميل
        ttk.Label(form_frame, text="اسم العميل:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # نوع العميل
        ttk.Label(form_frame, text="نوع العميل:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.type_combo = ttk.Combobox(form_frame, width=20, values=["عميل", "مورد", "أخرى"])
        self.type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.type_combo.set("عميل")

        # الهاتف
        ttk.Label(form_frame, text="الهاتف:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_entry = ttk.Entry(form_frame, width=20)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        # البريد الإلكتروني
        ttk.Label(form_frame, text="البريد الإلكتروني:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=20)
        self.email_entry.grid(row=1, column=3, padx=5, pady=5)

        # العنوان
        ttk.Label(form_frame, text="العنوان:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.address_entry = ttk.Entry(form_frame, width=20)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5)

        # الملاحظات
        ttk.Label(form_frame, text="ملاحظات:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.notes_entry = ttk.Entry(form_frame, width=20)
        self.notes_entry.grid(row=2, column=3, padx=5, pady=5)

        # أزرار التحكم
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="إضافة عميل", command=self.add_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تحديث", command=self.update_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حذف", command=self.delete_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="مسح الحقول", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        # جدول العملاء
        table_frame = ttk.LabelFrame(main_frame, text="قائمة العملاء", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("ID", "الاسم", "النوع", "الهاتف", "البريد الإلكتروني", "العنوان")
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        self.customers_tree.bind('<<TreeviewSelect>>', self.on_customer_selected)

        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_customers(self):
        """تحميل قائمة العملاء"""
        try:
            # مسح الجدول الحالي
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)

            customers = self.db.fetch_all('''
                                          SELECT customer_id, name, customer_type, phone, email, address
                                          FROM customers
                                          ORDER BY name
                                          ''')

            for customer in customers:
                self.customers_tree.insert("", tk.END, values=customer)

        except Exception as e:
            print(f"خطأ في تحميل العملاء: {str(e)}")

    def on_customer_selected(self, event):
        """عند اختيار عميل من الجدول"""
        selected_item = self.customers_tree.selection()
        if selected_item:
            customer_data = self.customers_tree.item(selected_item[0], 'values')
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, customer_data[1])
            self.type_combo.set(customer_data[2])
            self.phone_entry.delete(0, tk.END)
            self.phone_entry.insert(0, customer_data[3] or "")
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, customer_data[4] or "")
            self.address_entry.delete(0, tk.END)
            self.address_entry.insert(0, customer_data[5] or "")
            self.notes_entry.delete(0, tk.END)

    def add_customer(self):
        """إضافة عميل جديد"""
        name = self.name_entry.get()
        customer_type = self.type_combo.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        address = self.address_entry.get()
        notes = self.notes_entry.get()

        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم العميل")
            return

        try:
            # إنشاء معرف عميل جديد
            customer_id = f"CUST{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

            self.db.execute_query('''
                                  INSERT INTO customers (customer_id, name, customer_type, phone, email, address, notes,
                                                         created_date)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                  ''', (customer_id, name, customer_type, phone, email, address, notes,
                                        datetime.now().strftime('%Y-%m-%d')))

            messagebox.showinfo("نجاح", "تم إضافة العميل بنجاح")
            self.clear_fields()
            self.load_customers()
            self.parent_system.populate_tabs()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة العميل: {str(e)}")

    def update_customer(self):
        """تحديث بيانات العميل"""
        selected_item = self.customers_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يرجى اختيار عميل للتحديث")
            return

        customer_id = self.customers_tree.item(selected_item[0], 'values')[0]
        name = self.name_entry.get()
        customer_type = self.type_combo.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        address = self.address_entry.get()
        notes = self.notes_entry.get()

        try:
            self.db.execute_query('''
                                  UPDATE customers
                                  SET name          = ?,
                                      customer_type = ?,
                                      phone         = ?,
                                      email         = ?,
                                      address       = ?,
                                      notes         = ?
                                  WHERE customer_id = ?
                                  ''', (name, customer_type, phone, email, address, notes, customer_id))

            messagebox.showinfo("نجاح", "تم تحديث بيانات العميل بنجاح")
            self.load_customers()
            self.parent_system.populate_tabs()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحديث العميل: {str(e)}")

    def delete_customer(self):
        """حذف العميل"""
        selected_item = self.customers_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يرجى اختيار عميل للحذف")
            return

        customer_id = self.customers_tree.item(selected_item[0], 'values')[0]
        customer_name = self.customers_tree.item(selected_item[0], 'values')[1]

        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف العميل '{customer_name}'؟"):
            try:
                # التحقق إذا كان للعميل فواتير مرتبطة
                has_invoices = self.db.fetch_one('''
                                                 SELECT COUNT(*)
                                                 FROM sales
                                                 WHERE customer_id = ?
                                                 ''', (customer_id,))[0]

                if has_invoices > 0:
                    messagebox.showerror("خطأ", "لا يمكن حذف العميل لأنه لديه فواتير مرتبطة")
                    return

                self.db.execute_query('DELETE FROM customers WHERE customer_id = ?', (customer_id,))
                messagebox.showinfo("نجاح", "تم حذف العميل بنجاح")
                self.clear_fields()
                self.load_customers()
                self.parent_system.populate_tabs()

            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في حذف العميل: {str(e)}")

    def clear_fields(self):
        """مسح حقول الإدخال"""
        self.name_entry.delete(0, tk.END)
        self.type_combo.set("عميل")
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)


class ProductsManagementWindow:
    def __init__(self, root, db, parent_system):
        self.root = root
        self.db = db
        self.parent_system = parent_system

        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="إدارة المنتجات والمخزون",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # إطار الإضافة/التعديل
        form_frame = ttk.LabelFrame(main_frame, text="بيانات المنتج", padding="10")
        form_frame.pack(fill=tk.X, pady=10)

        # اسم المنتج
        ttk.Label(form_frame, text="اسم المنتج:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # الفئة
        ttk.Label(form_frame, text="الفئة:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.category_combo = ttk.Combobox(form_frame, width=20, values=[
            "ألعاب", "مستلزمات مكتبية", "أجهزة كهربائية", "ملابس", "أخرى"
        ])
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("أخرى")

        # سعر التكلفة
        ttk.Label(form_frame, text="سعر التكلفة:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.cost_entry = ttk.Entry(form_frame, width=20)
        self.cost_entry.grid(row=1, column=1, padx=5, pady=5)

        # سعر البيع
        ttk.Label(form_frame, text="سعر البيع:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.price_entry = ttk.Entry(form_frame, width=20)
        self.price_entry.grid(row=1, column=3, padx=5, pady=5)

        # الكمية الأولية
        ttk.Label(form_frame, text="الكمية الأولية:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(form_frame, width=20)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        # الحد الأدنى للمخزون
        ttk.Label(form_frame, text="الحد الأدنى للمخزون:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.min_stock_entry = ttk.Entry(form_frame, width=20)
        self.min_stock_entry.insert(0, "5")
        self.min_stock_entry.grid(row=2, column=3, padx=5, pady=5)

        # الملاحظات
        ttk.Label(form_frame, text="ملاحظات:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.notes_entry = ttk.Entry(form_frame, width=20)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=5)

        # أزرار التحكم
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=10)

        ttk.Button(button_frame, text="إضافة منتج", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تحديث", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="حذف", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="مسح الحقول", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تعديل المخزون", command=self.adjust_stock).pack(side=tk.LEFT, padx=5)

        # جدول المنتجات
        table_frame = ttk.LabelFrame(main_frame, text="قائمة المنتجات", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("ID", "الاسم", "الفئة", "سعر التكلفة", "سعر البيع", "المخزون", "المباع", "الحالة")
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_selected)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_products(self):
        """تحميل قائمة المنتجات"""
        try:
            # مسح الجدول الحالي
            for item in self.products_tree.get_children():
                self.products_tree.delete(item)

            products = self.db.fetch_all('''
                                         SELECT product_id,
                                                name,
                                                category,
                                                cost_price,
                                                selling_price,
                                                current_stock,
                                                quantity_sold
                                         FROM products
                                         ORDER BY name
                                         ''')

            for product in products:
                status = "منتهي" if product[5] == 0 else "منخفض" if product[5] < 5 else "جيد"
                self.products_tree.insert("", tk.END, values=(
                    product[0], product[1], product[2] or "",
                    f"{product[3]:.2f}", f"{product[4]:.2f}",
                    product[5], product[6], status
                ))

        except Exception as e:
            print(f"خطأ في تحميل المنتجات: {str(e)}")

    def on_product_selected(self, event):
        """عند اختيار منتج من الجدول"""
        selected_item = self.products_tree.selection()
        if selected_item:
            product_data = self.products_tree.item(selected_item[0], 'values')
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, product_data[1])
            self.category_combo.set(product_data[2] or "أخرى")
            self.cost_entry.delete(0, tk.END)
            self.cost_entry.insert(0, product_data[3])
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, product_data[4])
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, product_data[5])
            self.min_stock_entry.delete(0, tk.END)
            self.min_stock_entry.insert(0, "5")
            self.notes_entry.delete(0, tk.END)

    def add_product(self):
        """إضافة منتج جديد"""
        name = self.name_entry.get()
        category = self.category_combo.get()
        cost_price = self.cost_entry.get()
        selling_price = self.price_entry.get()
        quantity = self.quantity_entry.get()
        min_stock = self.min_stock_entry.get()
        notes = self.notes_entry.get()

        if not name or not cost_price or not selling_price:
            messagebox.showerror("خطأ", "يرجى إدخال البيانات الأساسية للمنتج")
            return

        try:
            cost_price = float(cost_price)
            selling_price = float(selling_price)
            quantity = int(quantity) if quantity else 0
            min_stock = int(min_stock) if min_stock else 5

            if cost_price < 0 or selling_price < 0 or quantity < 0:
                messagebox.showerror("خطأ", "يرجى إدخال قيم صحيحة")
                return

            # إنشاء معرف منتج جديد
            max_index = self.db.fetch_one("SELECT MAX(CAST(SUBSTR(product_id, 2) AS INTEGER)) FROM products")[0] or 100
            new_index = max_index + 1
            product_id = f"P{new_index:03d}"

            self.db.execute_query('''
                                  INSERT INTO products (product_id, name, category, cost_price, selling_price,
                                                        initial_quantity, current_stock, min_stock_level, notes,
                                                        last_updated)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                  ''', (product_id, name, category, cost_price, selling_price,
                                        quantity, quantity, min_stock, notes, datetime.now().strftime('%Y-%m-%d')))

            messagebox.showinfo("نجاح", "تم إضافة المنتج بنجاح")
            self.clear_fields()
            self.load_products()
            self.parent_system.populate_tabs()

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في الأسعار والكميات")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة المنتج: {str(e)}")

    def update_product(self):
        """تحديث بيانات المنتج"""
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يرجى اختيار منتج للتحديث")
            return

        product_id = self.products_tree.item(selected_item[0], 'values')[0]
        name = self.name_entry.get()
        category = self.category_combo.get()
        cost_price = self.cost_entry.get()
        selling_price = self.price_entry.get()
        min_stock = self.min_stock_entry.get()
        notes = self.notes_entry.get()

        try:
            cost_price = float(cost_price)
            selling_price = float(selling_price)
            min_stock = int(min_stock) if min_stock else 5

            self.db.execute_query('''
                                  UPDATE products
                                  SET name            = ?,
                                      category        = ?,
                                      cost_price      = ?,
                                      selling_price   = ?,
                                      min_stock_level = ?,
                                      notes           = ?,
                                      last_updated    = ?
                                  WHERE product_id = ?
                                  ''', (name, category, cost_price, selling_price, min_stock, notes,
                                        datetime.now().strftime('%Y-%m-%d'), product_id))

            messagebox.showinfo("نجاح", "تم تحديث بيانات المنتج بنجاح")
            self.load_products()
            self.parent_system.populate_tabs()

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في الأسعار")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في تحديث المنتج: {str(e)}")

    def delete_product(self):
        """حذف المنتج"""
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يرجى اختيار منتج للحذف")
            return

        product_id = self.products_tree.item(selected_item[0], 'values')[0]
        product_name = self.products_tree.item(selected_item[0], 'values')[1]

        if messagebox.askyesno("تأكيد الحذف", f"هل أنت متأكد من حذف المنتج '{product_name}'؟"):
            try:
                # التحقق إذا كان للمنتج مبيعات مرتبطة
                has_sales = self.db.fetch_one('''
                                              SELECT COUNT(*)
                                              FROM invoice_items
                                              WHERE product_id = ?
                                              ''', (product_id,))[0]

                if has_sales > 0:
                    messagebox.showerror("خطأ", "لا يمكن حذف المنتج لأنه لديه مبيعات مرتبطة")
                    return

                self.db.execute_query('DELETE FROM products WHERE product_id = ?', (product_id,))
                messagebox.showinfo("نجاح", "تم حذف المنتج بنجاح")
                self.clear_fields()
                self.load_products()
                self.parent_system.populate_tabs()

            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في حذف المنتج: {str(e)}")

    def adjust_stock(self):
        """تعديل كمية المخزون"""
        selected_item = self.products_tree.selection()
        if not selected_item:
            messagebox.showerror("خطأ", "يرجى اختيار منتج لتعديل المخزون")
            return

        product_id = self.products_tree.item(selected_item[0], 'values')[0]
        product_name = self.products_tree.item(selected_item[0], 'values')[1]
        current_stock = int(self.products_tree.item(selected_item[0], 'values')[5])

        # نافذة تعديل المخزون
        stock_window = tk.Toplevel(self.root)
        stock_window.title(f"تعديل مخزون {product_name}")
        stock_window.geometry("300x200")

        main_frame = ttk.Frame(stock_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=f"المنتج: {product_name}", font=("Arial", 11, "bold")).pack(pady=5)
        ttk.Label(main_frame, text=f"المخزون الحالي: {current_stock}").pack(pady=5)

        ttk.Label(main_frame, text="الكمية الجديدة:").pack(pady=5)
        new_stock_entry = ttk.Entry(main_frame, width=15)
        new_stock_entry.pack(pady=5)
        new_stock_entry.insert(0, str(current_stock))

        def save_new_stock():
            try:
                new_stock = int(new_stock_entry.get())
                if new_stock < 0:
                    messagebox.showerror("خطأ", "يرجى إدخال كمية صحيحة")
                    return

                # حساب الفرق لتحديث الكمية الأولية
                difference = new_stock - current_stock

                self.db.execute_query('''
                                      UPDATE products
                                      SET current_stock    = ?,
                                          initial_quantity = initial_quantity + ?
                                      WHERE product_id = ?
                                      ''', (new_stock, difference, product_id))

                messagebox.showinfo("نجاح", f"تم تعديل المخزون إلى {new_stock}")
                stock_window.destroy()
                self.load_products()
                self.parent_system.populate_tabs()

            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال رقم صحيح")

        ttk.Button(main_frame, text="حفظ", command=save_new_stock).pack(pady=10)
        ttk.Button(main_frame, text="إلغاء", command=stock_window.destroy).pack(pady=5)

    def clear_fields(self):
        """مسح حقول الإدخال"""
        self.name_entry.delete(0, tk.END)
        self.category_combo.set("أخرى")
        self.cost_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.min_stock_entry.delete(0, tk.END)
        self.min_stock_entry.insert(0, "5")
        self.notes_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainSalesSystem(root)
    root.mainloop()
