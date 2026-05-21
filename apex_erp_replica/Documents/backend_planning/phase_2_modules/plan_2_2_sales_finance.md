# Plan 2.2: Sales & Financial Transactions (Exhaustive Detail)

## 1. Scope & Objective
This document details the complex logic required to handle Sales Orders, their transformation into Invoices, and the subsequent payment processing. This transition is the most critical workflow in the ERP.

---

## 2. Transactional Workflows

### 2.1. Sales Order Submission (`sls_orders`)
- **Source**: `new_sales_order_form_spec.md`, `sales_order_details_spec.md`
- **Workflow**:
    1. Validate `customer_id` and `salesperson_id` exist.
    2. Check stock for every item in `items[]`.
    3. Calculate Totals: `subtotal`, `total_tax`, `grand_total` (Must match frontend math).
    4. Save Header to `sls_orders` and Items to `sls_order_items`.
    5. Set status to `Submitted`.

### 2.2. Invoice Generation (`fin_invoices`)
- **Trigger**: User clicks "Convert to Invoice" in Order Details view.
- **Source**: `new_invoice_form_spec.md`, `invoice_details_spec.md`
- **Logic**:
    1. Check if an invoice already exists for this `order_id` (Prevent duplicates).
    2. Copy data from `sls_orders` to `fin_invoices`.
    3. Set Invoice Status to `Unpaid`.
    4. Generate `invoice_number` (INV-YYYYMMDD-XXXX).

---

## 3. Atomic Database Requirements
The transition from Order to Invoice MUST use a **DB Transaction**.
```python
async def convert_order_to_invoice(order_id: UUID):
    async with db.begin():
        # 1. Update Order Status
        # 2. Create Invoice Record
        # 3. Log Audit Event
```

---

## 4. Key Functions & Locations
| Function Name | Location | Description |
| :--- | :--- | :--- |
| `submit_sales_order` | `controllers/sales_controller.py` | Handles POST requests for new orders. |
| `calculate_order_totals` | `services/calc_service.py` | Centralized math for tax and discounts. |
| `process_payment` | `controllers/finance_controller.py` | Updates Invoice status and triggers Ledger. |

---

## 5. Verification Steps
1. [ ] **Stock Locking Test**: Submit an order for 100 items when only 50 are in stock; verify rejection.
2. [ ] **Invoice Linkage Test**: Verify that the `fin_invoices` table correctly references the `sls_orders.id`.
3. [ ] **Grand Total Check**: Verify to the penny that `invoice_total` matches the sum of its items.
