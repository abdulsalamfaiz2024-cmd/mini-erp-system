# Non-Blind Implementation Plan: Dashboard Overview

## 1. UI Infrastructure Analysis
*Reference File: `index.html`*

The Dashboard Overview consists of four main data-driven zones. The following HTML structures must be targeted for dynamic binding:

### 1.1. Sales Order Summary (Card 1)
- **Container**: `.stats-grid > .card:nth-child(1)`
- **Value Placeholders**:
    - `Total Orders`: `.val` inside the first `.stat-item`. (Current: "1,250")
    - `New`: `.val` inside the second `.stat-item`. (Current: "150")
    - `Pending`: `.val` inside the third `.stat-item`. (Current: "50")
- **Visual**: `<path>` inside `.mini-chart svg`. The `d` attribute must be dynamically generated based on trend values.

### 1.2. Invoice Status (Card 2)
- **Container**: `.stats-grid > .card:nth-child(2)`
- **Value Placeholders**:
    - `Paid`: `.val` inside `.legend-item`. (Current: "950")
    - `Unpaid`: `.legend-item:nth-child(2) span:nth-child(2)`. (Current: "Unpaid: 250")
    - `Overdue`: `.legend-item:nth-child(3) span:nth-child(2)`. (Current: "Overdue: 50")
- **Visual**: `.donut-chart`. Requires CSS variable injection or SVG path updates for the ring.

### 1.3. Outstanding Payments Table
- **Container**: `.data-table tbody`
- **Structure**: Row `<tr>` containing:
    - `<td>` with `<a>` (Invoice ID)
    - `<td>` (Customer Name)
    - `<td>` (Amount)
    - `<td>` (Due Date)

### 1.4. Financial Performance Chart
- **Container**: `.bar-viz`
- **Structure**: Multiple `.bar-group` divs.
    - Child `.bar.revenue`: `style="height: X%"`
    - Child `.bar.expense`: `style="height: Y%"`
    - Child `.month-label`: `innerText = MonthName`

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/dashboard_spec.md`*

| Spec Key | API Endpoint | Linked UI Element |
| :--- | :--- | :--- |
| `total_orders` | `GET /api/v1/dashboard/summary` | Card 1 > Total Orders Val |
| `order_trend_values` | `GET /api/v1/dashboard/summary` | Card 1 > SVG Path `d` |
| `paid_count` | `GET /api/v1/dashboard/invoice-stats` | Card 2 > Paid Val |
| `invoice_id` | `GET /api/v1/payments/outstanding` | Table > Row > Col 1 |
| `revenue` | `GET /api/v1/dashboard/performance` | Bar Chart > .bar.revenue height |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Database Query Logic
1. **Summary**: `SELECT count(*) FROM sls_orders`. Filter by `status` for New/Pending.
2. **Trend**: Aggregate `sls_orders` count by day/week for the last 9 intervals.
3. **Invoices**: `SELECT status, count(*) FROM fin_invoices GROUP BY status`.
4. **Performance**: `SELECT month, sum(revenue), sum(expense) FROM fin_ledger GROUP BY month`.

### 3.2. Controller Functions (`Backend/controllers/dashboard_controller.py`)
- `get_summary_stats()`: Processes counts and trend arrays.
- `get_invoice_distribution()`: Groups by paid/unpaid/overdue.
- `get_performance_data()`: Comparative revenue/expense aggregation.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/dashboard.js`*

1. **Initialization**: On `DOMContentLoaded`, call `ApexAPI.getDashboardSummary()`.
2. **Path Generator**: Create a utility to convert `[10, 20, 30...]` into an SVG `L` path string.
3. **Row Template**:
```javascript
const rowTemplate = (item) => `
    <tr>
        <td><a href="Pages/invoice_details.html?id=${item.invoice_id}" class="invoice-link">${item.invoice_id}</a></td>
        <td>${item.customer_name}</td>
        <td>$${item.amount.toLocaleString()}</td>
        <td>${formatDate(item.due_date)}</td>
    </tr>`;
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `index.html`. Ensure the IDs used in `dashboard.js` match the selectors identified in Section 1.
2. [ ] **Data Range**: Backend must return exactly 6 months for the performance chart and 9 points for the trend line.
3. [ ] **Currency**: Ensure `amount` is formatted as `$X,XXX.XX` in the frontend before injection.
