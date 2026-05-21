# UI Redesign Map
Complete documentation of redesigned ERP user interface

## Architecture Overview

### Layout Structure
```
┌─────────────┬──────────────────────────────────────┐
│             │  Top Action Bar (Dynamic)            │
│             ├──────────────────────────────────────┤
│  Sidebar    │                                      │
│  (Fixed)    │  Content Area (Scrollable)           │
│             │                                      │
│             │                                      │
└─────────────┴──────────────────────────────────────┘
```

### Sidebar Navigation Sections
1. 📊 Dashboard
2. 🛒 Sales Orders
3. 🧾 Invoices
4. 💰 Finance
5. 💸 Expenses  
6. 📒 Ledger
7. 📦 Inventory
8. 🛍️ Purchasing
9. 📊 Accounting
10. 👥 Employees
11. 🤝 Customers
12. 🏢 Suppliers
13. 📈 Reports
14. ⚙️ Settings

---

## Page Details

### Sales Orders Page
**Location:** `ui/sales/sales_orders_page.py`

**Top Bar Actions:**
- 🆕 New Order
- 📤 Submit (disabled if no selection)
- 🧾 Invoice (disabled if no selection)
- 📑 Export

**Content:**
- Table showing all sales orders with columns: Order #, Date, Customer, Amount, Workflow State, Status
- Double-click to view/edit
- Row selection enables context-specific actions

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| New Order | `SalesOrderService.create_order` | ✅ IMPLEMENTED |
| Submit | `SalesOrderService.submit_order` | ✅ IMPLEMENTED |
| Invoice | `SalesManager.generate_invoice` | ✅ IMPLEMENTED |
| Export | `ReportingManager.export_to_csv` | ✅ IMPLEMENTED |
| Load Data | SQL Query | ✅ IMPLEMENTED |

---

### Invoices Page
**Location:** `ui/sales/invoices_page.py`

**Top Bar Actions:**
- 💰 Record Payment (disabled if no selection)
- 🖨️ Print (disabled if no selection)
- 📑 Export

**Content:**
- Table showing all invoices with columns: Invoice #, Date, Customer, Amount, Paid, Balance, Status
- Filters for paid/unpaid
- Payment tracking

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| Record Payment | `Sales Manager.record_payment` | ✅ IMPLEMENTED |
| Print | `ReportingManager.export_pdf_table` | ✅ IMPLEMENTED |
| Export | `ReportingManager.export_to_csv` | ✅ IMPLEMENTED |
| Load Data | SQL Query with JOIN to payments | ✅ IMPLEMENTED |

---

### Finance Page
**Location:** `ui/finance/finance_page.py` (refactored from `finance_ui.py`)

**Top Bar Actions:**
- ➕ New Expense
- ✅ Approve (with payment dialog)
- ❌ Reject
- 📑 Export

**Content:**
- P&L Dashboard
- Pending Approvals table
- Recent Expenses table

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| New Expense | `FinanceManager.add_expense` | ⏳ EXISTING (not refactored) |
| Approve | `SalesOrderService.approve_finance` | ⏳ EXISTING (with PaymentApprovalDialog) |
| Reject | `SalesOrderService.reject_order` | ⏳ EXISTING |
| Export | `ReportingManager.export_to_csv` | ⏳ EXISTING |
| Load P&L | `FinanceManager.get_profit_loss` | ⏳ EXISTING |

**Status:** Existing implementation needs refactoring to new layout

---

### Inventory Page
**Location:** `ui/inventory/inventory_page.py` (refactored from `inventory_ui.py`)

**Top Bar Actions:**
- 📦 Issue Order
- 🔄 Return
- 📊 Stock Count
- ➕ Add Product
- 📑 Export

**Content:**
- Stock statistics cards
- Stock levels table
- Pending warehouse releases

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| Issue Order | `InventoryManager.deduct_stock` | ⏳ EXISTING (needs wrapper) |
| Return | `InventoryManager.add_stock` | ⏳ EXISTING (needs wrapper) |
| Stock Count | Custom adjustment logic | ⚠️ PLACEHOLDER |
| Add Product | `InventoryManager.add_stock` | ⏳ EXISTING |
| Warehouse Release | `SalesOrderService.fulfill_order` | ⏳ EXISTING |
| Export | `ReportingManager.export_to_csv` | ⏳ EXISTING |

**Status:** Existing implementation needs refactoring to new layout

---

### Employees Page
**Location:** `ui/admin/employees_page.py` (refactored from `employee_ui.py`)

**Top Bar Actions:**
- ➕ New Employee
- ✏️ Edit (disabled if no selection)
- 🔐 Assign Permissions (disabled if no selection)
- 🚫 Deactivate (disabled if no selection)

**Content:**
- Employees table with columns: ID, Name, Department, Status, Approval Level
- Filter by status

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| New Employee | `EmployeeService.create_employee` | ⏳ EXISTING (needs refactor) |
| Edit | `EmployeeService.update_employee` | ⏳ EXISTING |
| Assign Permissions | `EmployeeService.assign_permissions` | ⏳ EXISTING |
| Deactivate | `EmployeeService.change_status` | ⏳ EXISTING |
| Load Data | `EmployeeService.list_employees` | ⏳ EXISTING |

**Status:** Existing implementation needs refactoring to new layout

---

### Customers Page
**Location:** Refactored from `crm_ui.py`

**Top Bar Actions:**
- ➕ New Customer
- 📊 Customer Report
- 📈 Segmentation

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| Customer Report | `CRMManager.get_customer_history` | ⏳ EXISTING |
| Segmentation | `CRMManager.get_customer_segmentation` | ⏳ EXISTING |
| Credit Check | `CRMManager.check_credit_limit` | ⏳ EXISTING |

**Status:** Existing implementation needs refactoring to new layout

---

### Reports Page
**Location:** Refactored from `reports_ui.py`

**Top Bar Actions:**
- 📊 Sales Report
- 📦 Inventory Report
- 🛍️ Purchase Report
- 📑 Export

**APIs Used:**
| Button/Action | API | Status |
|--------------|-----|--------|
| Sales Report | `ReportingManager.get_sales_report` | ⏳ EXISTING |
| Inventory Report | `ReportingManager.get_inventory_report` | ⏳ EXISTING |
| Purchase Report | `ReportingManager.get_purchase_report` | ⏳ EXISTING |
| Customer Statement | `ReportingManager.get_customer_statement` | ⏳ EXISTING |
| Export CSV | `ReportingManager.export_to_csv` | ⏳ EXISTING |
| Export Excel | `ReportingManager.export_to_excel` | ⏳ EXISTING |
| Export PDF | `ReportingManager.export_pdf_table` | ⏳ EXISTING |

**Status:** Existing implementation needs refactoring to new layout

---

## Pages Not Yet Implemented

### Accounting Module (Missing Backend APIs)
- **Journal Page** - requires accounting journal backend API
- **Trial Balance Page** - requires trial balance calculation API
- **Account Ledger Page** - can adapt from finance ledger

### Sales Returns
- **Returns Page** - requires sales return workflow backend API

### Inventory Adjustments
- **Adjustments Page** - can use existing APIs with negative quantities

---

## Implementation Status

### ✅ Completed Components
- `ui/layout/sidebar.py` - Vertical navigation with 14 sections
- `ui/layout/topbar.py` - Dynamic action bar with tooltip support
- `ui/layout/base_page.py` - Base class with API binding enforcement
- `ui/sales/sales_orders_page.py` - Full implementation with 4 API bindings
- `ui/sales/invoices_page.py` - Full implementation with 3 API bindings

### ⏳ Needs Refactoring
- Existing pages need to inherit from `BasePage`
- Existing pages need to populate topbar actions
- Remove tab-based navigation from main_window.py

### ⚠️ Requires New Backend
- Accounting module (3 pages)
- Sales returns workflow
- Inventory adjustment workflow

---

## Next Steps

1. **Refactor Main Window** - Replace tab navigation with sidebar + page router
2. **Migrate Existing Pages** - Refactor finance_ui, inventory_ui, employee_ui to new layout
3. **Create Missing Placeholders** - Stub accounting pages
4. **Testing** - Verify all navigation works
5. **API Coverage** - Ensure all 53 APIs are reachable from UI
