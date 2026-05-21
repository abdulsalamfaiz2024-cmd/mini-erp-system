# Non-Blind Implementation Plan: Expenses List

## 1. UI Infrastructure Analysis
*Reference File: `Pages/expenses_list.html`*

The Expenses List is a management table for operational spend. The following HTML structures must be targeted:

### 1.1. Summary Stats (4-Column Grid)
- **Container**: `.metrics-grid` (Lines 133-158).
- **Target Value Labels**:
    - Total: `.metrics-grid > .card:nth-child(1) .metric-value`
    - Approved: `.metrics-grid > .card:nth-child(2) .metric-value`
    - Pending: `.metrics-grid > .card:nth-child(3) .metric-value`
    - Rejected: `.metrics-grid > .card:nth-child(4) .metric-value`

### 1.2. Filters & Search
- **Search**: `.search-input-wrapper input` (Line 167).
- **Category Filter**: `select:nth-of-type(1)` (Line 169).
- **Status Filter**: `select:nth-of-type(2)` (Line 177).

### 1.3. Expenses Table
- **Table Body**: `.data-table tbody` (Line 203).
- **Row Architecture**:
    - `EXP-ID`: Col 1.
    - `Date`: Col 2.
    - `Description`: Col 3.
    - `Category`: Col 4.
    - `Submitted By`: Col 5.
    - `Amount`: Col 6 (font-weight: 600).
    - `Status`: Col 7 (containing `.status-badge` with class `approved|pending|overdue`).
    - `Actions`: Col 8 (containing `.action-links` spans for Edit/Delete).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/expenses_list_spec.md`*

| Spec Key | API JSON Path | Functional Match |
| :--- | :--- | :--- |
| `expenses[]` | `expenses` | `.data-table tbody` |
| `approved_count` | `summary.approved_count` | Metric Card 2 |
| `submitted_by` | `expenses[].submitted_by` | Col 5 |
| `status` | `expenses[].status` | Col 7 Badge Class |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Query Service
The expense list requires filtering on three optional parameters.
1. `GET /api/v1/expenses`:
    - `SELECT * FROM fin_expenses`
    - Apply `WHERE` clauses for `category_id`, `status`, and `substring(description)`.
    - Join `mst_users` to get the `submitted_by` name.
2. `DELETE /api/v1/expenses/{id}`:
    - Primary key deletion from `fin_expenses`.
    - **Security Rule**: User must be the author or have `FINANCE_ADMIN` role.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/expenses_list.js`*

1. **Badge Status Resolver**:
```javascript
function getBadgeClass(status) {
    if (status === 'Approved') return 'approved';
    if (status === 'Pending') return 'pending';
    return 'overdue'; // For Rejected
}
```
2. **Deletion Handler**:
```javascript
async function deleteExpense(id) {
    if (confirm(`Delete expense ${id}?`)) {
        const response = await ApexAPI.deleteExpense(id);
        if (response.success) refreshList();
    }
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/expenses_list.html`. Ensure the "Add Expense" button correctly targets `new_expense_form.html`.
2. [ ] **Currency Accuracy**: Ensure decimals are not rounded; `$285.50` must show exactly as is.
3. [ ] **Soft vs Hard Delete**: Verify if the business logic requires a "Soft Delete" (`is_active=False`) instead of a raw DB delete for audit purposes.
