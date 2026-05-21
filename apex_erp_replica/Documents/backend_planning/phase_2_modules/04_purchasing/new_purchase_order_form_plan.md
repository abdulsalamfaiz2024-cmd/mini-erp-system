# Non-Blind Implementation Plan: New Purchase Order Form

## 1. UI Infrastructure Analysis
*Reference File: `Pages/new_purchase_order_form.html`*

The New PO Form is the primary intake for procurement requests. The following HTML structures must be targeted:

### 1.1. Header Context
- **Breadcrumbs**: `.breadcrumbs` (Line 151).
- **Supplier Search**: `input` (Line 181). (Triggers `GET /api/purchasing/suppliers/search`).
- **PO Number**: `input[disabled]` (Line 190). (Shown as "Auto-generated").
- **Order Date**: `input[type="date"]` (Line 194).

### 1.2. Logistics & Terms
- **Payment Terms**: `select` (Line 210).
- **Delivery Date**: `input[type="date"]` (Line 218).
- **Address**: `textarea` (Line 223).

### 1.3. Line Item Engine (Table)
- **Table Body**: `.data-table tbody` (Line 247).
- **Interactive Row Fields**:
    - `Qty`: `input[type="number"]` (Line 250).
    - `Unit Price`: `input[type="text"]` (Line 251).
    - `Line Total`: `.data-table td:nth-child(4)` (Line 252).
- **Summary Block**: `.total-summary` (Line 268-274).
    - Targets: Subtotal, Tax, Shipping, Grand Total cells.

### 1.4. Submission Logic
- **Action Buttons**: `.form-footer` (Line 285-291).
    - Cancel, Save Draft, Submit for Approval.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/new_purchase_order_form_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `supplier_id` | `root.supplier_id` | Value resolved from Search Input selection |
| `line_items[]` | `line_items` | Mapped from rows in `.data-table tbody` |
| `tax` | `root.tax` | Calculated field (8%) in Summary block |
| `grand_total` | `root.grand_total` | Final calculated sum |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Procurement Draft Logic
1. `GET /api/purchasing/suppliers/search?q={query}`:
    - Search `mst_suppliers` for name matches.
2. `POST /api/purchasing/pos/create`:
    - **Header Record**: Insert into `pur_purchase_orders` with `status='Pending Approval'`.
    - **Line Items**: Bulk insert into `pur_po_items`.
    - **Finance Placeholder**: Create a pending commitment in the general ledger (optional).

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/new_purchase_order_form.js`*

1. **Reactive Calculator**:
```javascript
function recalculate() {
    let subtotal = 0;
    document.querySelectorAll('tbody tr').forEach(row => {
        const qty = parseFloat(row.querySelector('input[type="number"]').value) || 0;
        const price = parseFloat(row.querySelector('input[type="text"]').value.replace('$', '')) || 0;
        const lineTotal = qty * price;
        row.querySelector('.line-total').textContent = '$' + lineTotal.toFixed(2);
        subtotal += lineTotal;
    });
    // Update summary labels...
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/new_purchase_order_form.html`. Confirm that the "Subtotal" label in JS matches the class structure at Line 269.
2. [ ] **Precision**: All currency inputs should handle the `$` prefix during text entry.
3. [ ] **Validation**: Ensure "Submit for Approval" (Line 289) is blocked if the `supplier_id` has not been resolved from search.
