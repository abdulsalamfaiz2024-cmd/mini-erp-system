# Page Implementation Plan: Customer Profile (Master Data)

## 1. Scope & Objective
Exhaustive blueprint for the 360-degree view of a Customer. This serves as the source of truth for billing, shipping, and relationship history.

---

## 2. API Data Aggregation (Exhaustive)
Based on `customer_profile_spec.md`.

### 2.1. The "Total Relationship" Object
The backend must synthesize data from Sales, Finance, and Returns for this view.

| Key | Calculation | Description |
| :--- | :--- | :--- |
| `profile` | `mst_customers` table | Address, Contact, Tax ID. |
| `stats.total_orders` | `COUNT(sls_orders)` | Global order volume. |
| `stats.total_spent` | `SUM(fin_invoices.total_amount)` | Total lifetime value (LTV). |
| `stats.outstanding` | `SUM(unpaid invoices)` | Total currently owed to Apex ERP. |
| `recent_orders` | `SELECT TOP 5 from sls_orders` | Quick view of active history. |

---

## 3. Controller Logic: `update_customer_profile`
This page handles both "View" and "Edit" modes.

1. **Step A: Validation**:
    - Email must be valid and not taken by another user.
    - `credit_limit` cannot be negative.
2. **Step B: Conflict Check**: 
    - If a Customer is being deactivated (`is_active=False`), verify they have ZERO outstanding `fin_invoices`.
3. **Step C: Update Execution**: 
    - Atomic update to the `mst_customers` table.
    - Log an audit event: "User [ID] updated billing address for Customer [ID]".

---

## 4. UI Interconnection Details
- **Google Maps Link**: (Optional) Backend returns a formatted string for the frontend to open a map to the `shipping_address`.
- **Primary Actions**:
    - "New Order": Navigates to `new_sales_order_form.html?customer_id=[ID]`.
    - "Statement": Triggers a `services/reporting` call to generate a PDF account statement.

---

## 5. Security & Permission Matrix
- **View**: All staff.
- **Edit Details**: `SALES`, `ADMIN`.
- **Edit Financials (Credit Limit)**: Only `FINANCE_MANAGER` or `ADMIN`.

---

## 6. Verification Steps
1. [ ] **Stat Sync**: Create a new $1000 invoice; verify the Customer Profile "Outstanding" balance increases by exactly $1000.
2. [ ] **Uniqueness Test**: Attempt to update a customer to use an email already in the database; verify `409 Conflict`.
3. [ ] **Audit Trail**: Verify that manual changes to the `credit_limit` are recorded in the system logs.
