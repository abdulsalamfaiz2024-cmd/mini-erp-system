# Non-Blind Implementation Plan: Returns Dashboard

## 1. UI Infrastructure Analysis
*Reference File: `Pages/returns_dashboard.html`*

The Returns Dashboard is the command center for reverse logistics. The following HTML structures must be targeted:

### 1.1. Executive Controls
- **New Request Button**: `.btn.btn-blue` (Line 176).
- **Export Utility**: `.btn.btn-gray` (Line 175).

### 1.2. KPI Ribbon (4-Column Grid)
- **Container**: `.returns-metrics` (Line 181).
- **Metric Targets**:
    - Pending: `.card:nth-child(1) .metric-value`. (Line 185).
    - Refund Value: `.card:nth-child(2) .metric-value`. (Line 192).
    - Avg Time: `.card:nth-child(3) .metric-value`. (Line 199).
    - Return Rate: `.card:nth-child(4) .metric-value`. (Line 206).

### 1.3. Distribution & Analytics
- **Reason Breakdown**: `.reason-item` group (Line 241).
    - Logic: Update `.reason-bar-fill` width style based on percentage.
- **Trend Chart**: Bar container at Line 220. (Requires generation of dynamic divs for last 30 days).

### 1.4. Activity Register
- **Table Body**: `.data-table tbody` (Line 285).
- **Row Architecture**:
    - `Return ID`: Col 1 (font-weight: 600).
    - `Customer`: Col 2.
    - `Date`: Col 3.
    - `Reason`: Col 4.
    - `Status`: Col 5 (pill classes: `pending|authorized|rejected`).
    - `Action`: Col 6 (View button).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/returns_dashboard_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `refund_total_value` | `root.refund_total_value` | Metric 2 Value |
| `avg_processing_days`| `root.avg_processing_days` | Metric 3 Value |
| `recent_returns[]` | `recent_returns` | Table rows mapping |
| `status` | `recent_returns[].status` | Map text to pill class (AUTHORIZED -> authorized) |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Reverse Logistics Analytics
1. `GET /api/v1/returns/summary`:
    - Count rows in `log_returns` by status.
    - Calculate sum of `refund_amount` for processing state.
    - Calculate `avg(completed_at - created_at)` for process time.
2. `GET /api/v1/returns/analytics/reasons`:
    - `SELECT reason, (COUNT(*) * 100 / total) as pct FROM log_returns GROUP BY reason`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/returns_dashboard.js`*

1. **Reason Bar Renderer**:
```javascript
function renderReasons(reasons) {
    const container = document.querySelector('.card:has(.reason-item)');
    // Empty and rebuild reason items with dynamic widths...
}
```
2. **Auto-Refresh**: Dashboard polls analytics every 5 minutes to stay live.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/returns_dashboard.html`. Confirm that the "Create Return" button (Line 176) correctly routes to `new_return_request.html`.
2. [ ] **Precision**: Refund Value metric (Line 192) must include the dollar sign and 2 decimal precision.
3. [ ] **Integrity**: Ensure the "Authorized" status pill (Line 56) uses the `status-pill authorized` class for consistency with the design system.
