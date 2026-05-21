# Non-Blind Implementation Plan: Invoice Details

## 1. UI Infrastructure Analysis
*Reference File: `Pages/invoice_details.html`*

The Invoice Details page is the financial record for a transaction. The following HTML structures must be targeted:

### 1.1. Header & Financial Summary
- **Main Heading**: `.page-title` (Line 129).
- **Invoice Summary Meta**: (Line 131)
    - `Invoice #`: `INV-2024-1098` segment.
    - `Status`: `span` with color `var(--accent-red)`. (Line 131).

### 1.2. Action Buttons
- **Record Payment**: `.btn.btn-green` (Line 139). Triggers the financial update.
- **Send Reminder**: `.btn.btn-blue` (Line 140).

### 1.3. Logic Configuration
- **Invoice Information Card**: `.card-body` (Line 154).
    - `Date Issued`: `.info-row:nth-child(1) .info-value`
    - `Due Date`: `.info-row:nth-child(2) .info-value`
    - `Sales Order Ref`: `.info-row:nth-child(3) .info-value`
- **Customer Information Card**: `.card-body` (Line 185).
    - `Bill To`, `Contact`, `Address`, `Email`, `Phone`.

### 1.4. Tables
- **Line Items Table**: `.data-table tbody` (Line 216).
- **Payment History Card**: (Lines 283-287). Currently showing "No payments recorded yet." Logic must replace this with a table if `data.payments[]` is not empty.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/invoice_details_spec.md`*

| Spec Key | UI Selector | Business Logic |
| :--- | :--- | :--- |
| `invoice_id` | `invoice-title-span` | Must match URL parameter `?id=INV-XXX` |
| `status` | `span[style*="accent-red"]` | If `balance_due > 0` AND `due_date < today` -> "Overdue" |
| `items[]` | `.data-table tbody` | Must include `tax` per row as per JSON spec. |
| `balance_due` | `summary-row` (Last child) | `grand_total - amount_paid`. |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Financial Orchestration
Invoice data is tied to both Sales (Orders) and Finance (Ledger).
1. `GET /api/v1/invoices/{id}`:
    - Query `fin_invoices`.
    - Join `sls_orders` for the `sales_order_ref`.
    - Join `mst_customers` for profile data.
    - Aggregate `items` from `fin_invoice_items`.

### 3.2. Controller Logic: `record_payment`
1. **Validation**: Ensure `payment_amount <= balance_due`.
2. **Persistence**:
    - Update `fin_invoices.amount_paid`.
    - If `remaining == 0`, Update `fin_invoices.status = 'Paid'`.
    - Create a row in `fin_payments` (The historical tracking).
    - **Finance Event**: Update `fin_ledger` (Debit Cash / Credit Accounts Receivable).

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/invoice_details.js`*

1. **State Management**:
```javascript
function renderPayments(payments) {
    const container = document.querySelector('.payment-history-container');
    if (payments.length === 0) {
        container.innerHTML = '<div class="empty-msg">No payments recorded yet.</div>';
    } else {
        // Render history table...
    }
}
```
2. **Color Context**:
```javascript
function getStatusStyle(status) {
    const map = { 'Paid': 'var(--accent-green)', 'Overdue': 'var(--accent-red)', 'Pending': 'var(--accent-blue)' };
    return map[status] || 'gray';
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/invoice_details.html`. Ensure the "Sales Order Ref" link targets `sales_order_details.html?id=[REF]`.
2. [ ] **Financial Logic**: Backend MUST return `balance_due` calculated as a high-precision decimal.
3. [ ] **Atomic Payment**: Verify that "Record Payment" is a single transaction (Updates invoice + Adds history row).
