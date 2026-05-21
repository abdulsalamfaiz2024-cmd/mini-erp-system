# Non-Blind Implementation Plan: Financial Reports

## 1. UI Infrastructure Analysis
*Reference File: `Pages/financial_reports.html`*

The Financial Reports page is a high-level analytical dashboard. The following HTML structures must be targeted:

### 1.1. Parameter Filters
- **Report Type**: `select` (Line 148).
- **Reporting Period**: `select` (Line 156).
- **Comparison**: `select` (Line 164).
- **Generate Button**: `.btn.btn-blue` (Line 170) with text "Generate".

### 1.2. Executive Summary (3-Column Metrics)
- **Container**: `.metrics-grid` (Lines 178-200).
- **Target Value Labels**:
    - Revenue: Metric 1. (Line 182).
    - Gross Profit: Metric 2. (Line 189).
    - Net Income: Metric 3. (Line 196).

### 1.3. Report Table (Dynamic Statement)
- **Table Body**: `.data-table tbody` (Line 218).
- **Row Multi-Structure**:
    - `Category Header`: Style `background: #fcfcfc; font-weight: 600;` (Line 230).
    - `Line Item`: Style `padding-left: 40px;` (Line 234).
    - `Category Total`: Style `font-weight: 600; background: #f5f7f9;` (Line 247).
    - `Final Statement Bottom`: Style `font-weight: 700; background: #edf2f7;` (Line 282).
- **Variance Logic**: Text color `#22c55e` (Green) for positive or `#ef4444` (Red) for negative changes.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/financial_reports_spec.md`*

| Spec Key | API JSON Path | UI Representation |
| :--- | :--- | :--- |
| `summary_metrics` | `summary_metrics.net_income` | Net Income Metric Card |
| `report_data` | `report_data[]` | Recursive Row Injection into Tbody |
| `variance` | `items[].variance` | Colored text in Col 4 |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Reporting Engine Logic
The report type (Income Statement vs Balance Sheet) determines the SQL template.
1. `GET /api/v1/finance/reports`:
    - Fetch parameters from Query String.
    - If `income_statement`: Sum `Revenue` group matches vs `Expense` group matches from `fin_ledger`.
    - Join `mst_accounts` to determine which accounts fall into which report category.
2. `GET /api/v1/finance/reports/export`:
    - Generate HTML template from DB results.
    - Use `pdfkit` or `ReportLab` to convert to PDF.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/financial_reports.js`*

1. **Recursive Renderer**:
```javascript
function renderCategory(categoryObj) {
    let rows = `<tr class="header-row"><td colspan="5">${categoryObj.category}</td></tr>`;
    categoryObj.items.forEach(item => {
        rows += `
            <tr>
                <td style="padding-left:40px;">${item.name}</td>
                <td class="num">${item.current}</td>
                <td class="num">${item.prior}</td>
                <td class="num ${item.variance >= 0 ? 'green' : 'red'}">${item.variance}</td>
                <td class="num">${item.pct_change}%</td>
            </tr>`;
    });
    // Add Total row...
    return rows;
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/financial_reports.html`. Ensure the Generate button triggers the refresh without page reload (AJAX).
2. [ ] **Double Entry Verification**: Revenue - COGS - Expenses MUST match the Net Income figure displayed in the metric card.
3. [ ] **PDF Consistency**: Exported report must retain the same visual grouping (indents and bolds) as the web table.
