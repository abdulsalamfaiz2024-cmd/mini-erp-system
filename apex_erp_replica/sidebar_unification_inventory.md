# Sidebar Unification Inventory

| Page Name | HTML Path | Primary Associated API(s) |
| :--- | :--- | :--- |
| **Dashboard Overview** | `index.html` | `GET /api/v1/dashboard/summary`, `GET /api/v1/dashboard/invoice-stats` |
| **Sales Order Details** | `Pages/sales_order_details.html` | `GET /api/v1/sales/orders/{id}` |
| **New Sales Order Form** | `Pages/new_sales_order_form.html` | `GET /api/v1/customers`, `POST /api/v1/sales/orders` |
| **Invoice Details** | `Pages/invoice_details.html` | `GET /api/v1/finance/invoices/{id}` |
| **New Invoice Form** | `Pages/new_invoice_form.html` | `GET /api/v1/sales/orders/pending`, `POST /api/v1/finance/invoices` |
| **Customers** | `Pages/customers.html` | `GET /api/v1/customers` |
| **Finance Dashboard** | `Pages/finance_dashboard.html` | `GET /api/v1/finance/summary` |
| **Expenses List** | `Pages/expenses_list.html` | `GET /api/v1/finance/expenses` |
| **New Expense Form** | `Pages/new_expense_form.html` | `POST /api/v1/finance/expenses` |
| **Financial Reports** | `Pages/financial_reports.html` | `GET /api/v1/finance/reports` |
| **General Ledger** | `Pages/general_ledger.html` | `GET /api/v1/finance/ledger` |
| **Journal Entries** | `Pages/journal_entries.html` | `GET /api/v1/finance/journal` |
| **Inventory Dashboard** | `Pages/inventory_dashboard.html` | `GET /api/v1/inventory/summary` |
| **Product List** | `Pages/product_list.html` | `GET /api/v1/products` |
| **Product Details** | `Pages/product_details.html` | `GET /api/v1/products/{id}` |
| **Stock Adjustment** | `Pages/stock_adjustment.html` | `POST /api/v1/inventory/adjustments` |
| **Goods Receipt** | `Pages/goods_receipt.html` | `POST /api/v1/inventory/goods-receipt` |
| **Warehouse Locations** | `Pages/warehouse_locations.html` | `GET /api/v1/warehouses` |
| **Purchasing Dashboard** | `Pages/purchasing_dashboard.html` | `GET /api/v1/purchasing/summary` |
| **Purchase Order List** | `Pages/purchase_order_list.html` | `GET /api/v1/purchasing/orders` |
| **Purchase Order Details** | `Pages/purchase_order_details.html` | `GET /api/v1/purchasing/orders/{id}` |
| **New Purchase Order Form** | `Pages/new_purchase_order_form.html` | `POST /api/v1/purchasing/orders` |
| **Suppliers List** | `Pages/suppliers_list.html` | `GET /api/v1/purchasing/suppliers` |
| **Supplier Details** | `Pages/supplier_details.html` | `GET /api/v1/purchasing/suppliers/{id}` |
| **Returns Dashboard** | `Pages/returns_dashboard.html` | `GET /api/v1/returns/summary` |
| **Returns List** | `Pages/returns_list.html` | `GET /api/v1/returns` |
| **Return Details** | `Pages/return_details.html` | `GET /api/v1/returns/{id}` |
| **New Return Request** | `Pages/new_return_request.html` | `POST /api/v1/returns` |
| **Logistics & Inspection** | `Pages/logistics_inspection.html` | `PATCH /api/v1/returns/{id}/inspection` |
| **Credit Processing** | `Pages/credit_processing.html` | `POST /api/v1/returns/{id}/settle` |
