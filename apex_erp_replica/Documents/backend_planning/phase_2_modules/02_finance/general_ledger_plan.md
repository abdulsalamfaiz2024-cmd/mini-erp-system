# Non-Blind Implementation Plan: General Ledger

## 1. UI Infrastructure Analysis
*Reference File: `Pages/general_ledger.html`*

The General Ledger is a read-only summary of the system's financial health. The following HTML structures must be targeted:

### 1.1. Fiscal Context
- **Period Info**: `.action-header p` (Line 184). (Current: "Fiscal Year 2024 - Q3 • Period 9")

### 1.2. Metric Cards (5-Column Grid)
- **Container**: `.metrics-grid` (Lines 202-236).
- **Target Value Labels**:
    - Assets: `.metrics-grid > .card:nth-child(1) .metric-value`
    - Liabilities: `.metrics-grid > .card:nth-child(2) .metric-value`
    - Equity: `.metrics-grid > .card:nth-child(3) .metric-value`
    - Revenue: `.metrics-grid > .card:nth-child(4) .metric-value`
    - Expenses: `.metrics-grid > .card:nth-child(5) .metric-value`
- **Trend Tags**: Small `div` below value for percentage change (e.g., Line 206).

### 1.3. Accounts Table
- **Table Body**: `.data-table tbody` (Line 264).
- **Dynamic Columns**:
    - `CODE`: Col 1.
    - `ACCOUNT NAME`: Col 2 (font-weight: 500).
    - `CATEGORY`: Col 3 (Requires `category-tag` classes like `tag-asset`, `tag-liability`).
    - `DEBIT/CREDIT`: Cols 4 & 5.
    - `BALANCE`: Col 6 (font-weight: 600).
- **Action**: `👁️` eye icon must navigate to `account_details.html?id=[code]`.

### 1.4. Controls
- **Search**: `input[placeholder="Search accounts..."]` (Line 244).
- **Time Filter**: `select` (Line 246).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/general_ledger_spec.md`*

| Spec Key | API JSON Path | Linked UI Context |
| :--- | :--- | :--- |
| `summary` | `summary.total_assets` | Card 1 Metric Val |
| `accounts[]` | `accounts[].category` | Tab Badge Style (Line 52+) |
| `balance` | `accounts[].balance` | Col 6 (Red if negative) |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Complex Aggregation Logic
The GL Overview is essentially a summary of the `fin_ledger` table grouped by `account_id`.
1. `GET /api/v1/finance/ledger/summary`:
    - Sum debits and credits for all accounts where type is Asset, Liability, etc.
    - Calculate percentage change by comparing with the previous month's snapshot.
2. `GET /api/v1/finance/ledger/accounts`:
    - Join `mst_accounts` with categorized `fin_ledger` sums.
    - Support pagination as per Line 322 in HTML.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/general_ledger.js`*

1. **Tag Mapper**:
```javascript
const categoryMap = {
    'Asset': 'tag-asset',
    'Liability': 'tag-liability',
    'Equity': 'tag-equity',
    'Revenue': 'tag-revenue',
    'Expense': 'tag-expense'
};
```
2. **Formatting Logic**:
```javascript
function formatBalance(val) {
    if (val < 0) return `<span class="red-text">(${Math.abs(val).toLocaleString()})</span>`;
    return val.toLocaleString();
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/general_ledger.html`. Ensure the metrics grid correctly uses `repeat(5, 1fr)`.
2. [ ] **Ledger Integrity**: The sum of `Asset Metrics` - `Liability Metrics` must mathematically equal the `Equity Metric`.
3. [ ] **Performance**: Since the GL scans the entire ledger, ensure the backend endpoint is optimized with indexes on `account_id` and `entry_date`.
