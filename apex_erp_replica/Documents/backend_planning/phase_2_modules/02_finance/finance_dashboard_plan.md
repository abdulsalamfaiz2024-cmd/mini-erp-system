# Non-Blind Implementation Plan: Finance Dashboard

## 1. UI Infrastructure Analysis
*Reference File: `Pages/finance_dashboard.html`*

The Finance Dashboard is the strategic cockpit for fiscal health. The following HTML structures must be targeted:

### 1.1. KPI Matrix (Metrics Grid)
- **Container**: `.metrics-grid` (Line 129).
- **Metric Targets**:
    - Revenue: (Line 135).
    - Expenses: (Line 145).
    - Profit: (Line 155).
    - Cash Flow: (Line 166).
- **Trend Indicators**: (Lines 136, 146, 156, 167). (Uses hex codes `#22c55e` and `#ef4444`).

### 1.2. Operations Launchpad
- **Quick Actions**: `.quick-actions-grid` (Line 180).
    - Map buttons to respective files: `expenses_list.html`, `new_expense_form.html`, etc.

### 1.3. Ledger Sampling (Recent Transactions)
- **Table Body**: `.data-table tbody` (Line 216).
- **Row Architecture**:
    - `Date`: Col 1.
    - `Description`: Col 2.
    - `Account`: Col 3.
    - `Type`: Col 4 (badge classes: `type-badge in|out`).
    - `Amount`: Col 5 (color-coded currency: green for credit, red for debit).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/finance_dashboard_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `total_revenue` | `root.total_revenue` | Metric 1 Value |
| `net_profit` | `root.net_profit` | Metric 3 Value |
| `transactions[]` | `transactions` | Ledger table mapping |
| `type` | `transactions[].type` | Map to `in` (CREDIT) or `out` (DEBIT) badge classes |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Fiscal Aggregation Service
1. `GET /api/v1/finance/summary`:
    - Calculate `sum(amount)` for revenue accounts (4xxxx).
    - Calculate `sum(amount)` for expense accounts (5xxxx).
    - Delta calculations against previous month historical table.
2. `GET /api/v1/finance/transactions`:
    - `SELECT * FROM fin_ledger ORDER BY created_at DESC LIMIT 10`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/finance_dashboard.js`*

1. **Transaction Type Styling**:
```javascript
function getBadgeClass(type) {
    return type === 'CREDIT' ? 'type-badge in' : 'type-badge out';
}
function getAmountStyle(type) {
    return type === 'CREDIT' ? 'color: #166534;' : 'color: #991b1b;';
}
```
2. **Dynamic Period**: Updates page context label based on `root.period` (Line 31 of spec).

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/finance_dashboard.html`. Confirm that the "View All" link (Line 202) routes to `general_ledger.html`.
2. [ ] **Precision**: Verify that DEBIT amounts (Line 229) are displayed with a minus sign and RED styling.
3. [ ] **Integrity**: Ensure the "Cash Flow" metric icon (Line 163) uses the purple gradient as seen in the HTML inline style.
