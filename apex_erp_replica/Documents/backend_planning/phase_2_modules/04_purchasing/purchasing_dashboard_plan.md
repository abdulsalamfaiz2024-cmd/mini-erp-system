# Non-Blind Implementation Plan: Purchasing Dashboard

## 1. UI Infrastructure Analysis
*Reference File: `Pages/purchasing_dashboard.html`*

The Purchasing Dashboard is the procurement control center. The following HTML structures must be targeted:

### 1.1. Top-Level Actions
- **View Orders Button**: (Line 198).
- **Manage Suppliers**: (Line 200).
- **New PO Button**: (Line 202).

### 1.2. Metric Ribbon (4-Column Grid)
- **Container**: `.purchasing-metrics` (Line 207).
- **Target Value Labels**:
    - Pending: `.card:nth-child(1) .metric-value`. (Line 211).
    - To Be Received: `.card:nth-child(2) .metric-value`. (Line 219).
    - Overdue: `.card:nth-child(3) .metric-value`. (Line 227).
    - Monthly Spend: `.card:nth-child(4) .metric-value`. (Line 235).
- **Trends**: `.trend-up` / `.trend-down` spans within each card. (Lines 212, 220).

### 1.3. Analytics Charts
- **Budget Progress**: `.budget-bar-fill` (Line 54). `width` style based on `spend / budget` ratio.
- **Budget Text**: (Line 249). "$75,000 / $100,000".
- **Status Donut**: `.donut-chart` (Line 285). `background` conic-gradient depends on status count percentages.

### 1.4. Recent Activity
- **Table Body**: `.data-table tbody` (Line 325).
- **Row Architecture**:
    - `PO #`: Col 1.
    - `Supplier`: Col 2.
    - `Status`: Col 3 (Badge pill with color class `approved|shipped|pending|invoiced`).
    - `Date`: Col 4.
    - `Amount`: Col 5 (font-weight: 600).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/purchasing_dashboard_spec.md`*

| Spec Key | API JSON Path | UI Target |
| :--- | :--- | :--- |
| `pending_approval_count` | `root.pending_approval_count` | Metric 1 Value |
| `monthly_spend_amount` | `root.monthly_spend_amount` | Metric 4 Value |
| `recent_pos[]` | `recent_pos` | `.data-table tbody` |
| `status` | `recent_pos[].status` | Pill CSS class |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Procurement Metrics Engine
1. `GET /api/purchasing/dashboard/metrics`:
    - Count rows in `pur_purchase_orders` grouped by state (pending, overdue).
    - Calculate monthly spend: `SUM(total_amount)` for current month vs prior month for trend calculation.
2. `GET /api/purchasing/dashboard/spend-vs-budget`:
    - Aggregate PO totals vs `pur_budgets` table records.

### 3.2. List Aggregation
1. `GET /api/purchasing/dashboard/recent-pos`:
    - Query `pur_purchase_orders` join `mst_suppliers`.
    - Limit 5, Sort by `created_at DESC`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/purchasing_dashboard.js`*

1. **Donut Calculation**:
```javascript
function drawDonut(counts) {
    const total = counts.approved + counts.shipped + counts.draft;
    const appPct = (counts.approved / total) * 360;
    const shipPct = (counts.shipped / total) * 360;
    const chart = document.querySelector('.donut-chart');
    chart.style.background = `conic-gradient(var(--accent-blue) 0 ${appPct}deg, #2ecc71 ${appPct}deg ${appPct + shipPct}deg, #f1c40f ${appPct+shipPct}deg 360deg)`;
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/purchasing_dashboard.html`. Ensure the budget bar fill correctly maps the $75k/$100k example to 75% width.
2. [ ] **Precision**: Verify that the "Monthly Spend" metric displays 2 decimal places.
3. [ ] **Navigation**: Confirm that clicking any PO row triggers a redirect with the correct ID.
