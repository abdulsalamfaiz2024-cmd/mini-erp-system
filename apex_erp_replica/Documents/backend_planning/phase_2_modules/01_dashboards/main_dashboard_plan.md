# Non-Blind Implementation Plan: Dashboard Overview

## 1. UI Infrastructure Analysis
*Reference File: `index.html`*

The Root Dashboard is the primary entry point for all organizational visibility. The following HTML structures must be targeted:

### 1.1. Contextual Summary (Top Cards)
- **Sales Summary**: `.stats-grid .card:nth-child(1)` (Line 134).
    - Status Points: Total, New, Pending (Lines 140, 144, 148).
    - Trend Viz: `svg path` (Line 153). (Requires dynamic `d` attribute generation).
- **Invoicing Donut**: `.stats-grid .card:nth-child(2)` (Line 160).
    - Legend Targets: Paid, Unpaid, Overdue (Lines 167, 171, 175).

### 1.2. Operations Portal (Quick Actions)
- **Action Buttons**: `.action-buttons .action-btn` (Line 188, 191).
    - Destinations: `new_sales_order_form.html` and `new_invoice_form.html`.

### 1.3. Analytics Layer (Bottom Grid)
- **Receivables Ledger**: `.data-table tbody` (Line 214). (Outstanding Payments).
    - Link Logic: `a` tag (Line 216) targets `Pages/invoice_details.html`.
- **Fiscal Performance**: `.bar-viz` (Line 266).
    - Logic: Update `.bar.revenue` and `.bar.expense` heights (Lines 268-295) for Jan-Jun months.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/dashboard_spec.md`*

| Spec Key | API JSON Path | Functional UI Mapping |
| :--- | :--- | :--- |
| `order_trend_values` | `root.order_trend_values` | SVG sparkline path data |
| `paid_count` | `root.paid_count` | Donut legend entry 1 |
| `invoice_id` | `[].invoice_id` | Outstanding Table Col 1 |
| `revenue` | `performance.revenue` | Bar height % |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Executive Reporting Engine
1. `GET /api/v1/dashboard/summary`:
    - Aggregate counts from `pur_sales_orders` where status is 'new' or 'pending'.
2. `GET /api/v1/dashboard/performance`:
    - Calculate monthly totals for ledger entries categorized as revenue/expense for the last 6 months.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/dashboard.js`*

1. **Sparkline Engine**:
```javascript
function updateSparkline(values) {
    const path = document.querySelector('.mini-chart path');
    // Generate SVG path string from array...
}
```
2. **Dynamic Charting**: Manual height updates for CSS bars to ensure premium visual performance without heavy chart libraries.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `index.html`. Confirm that "Invoice ID" in the table (Line 211) utilizes the standard blue accent color.
2. [ ] **Precision**: Verify that the "Outstanding Payments" table (Line 214) displays amounts with two decimal points.
3. [ ] **Integrity**: Ensure the SVG sparkline (Line 152) scales correctly within its container.
