# Page Specification: Financial Reports

## 1. Overview
The Financial Reports page allows users to generate, view, and export key financial statements such as Income Statements (Profit & Loss), Balance Sheets, and Cash Flow Statements. It includes deep filtering options for reporting periods and comparison data.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Report Type Dropdown** | `report_type` | `GET /api/v1/finance/reports/types` | `GET` |
| **Reporting Period** | `start_date`, `end_date` | `GET /api/v1/finance/reports` | `GET` |
| **Compare With Dropdown** | `comparison_type` | `GET /api/v1/finance/reports` | `GET` |
| **Metric Cards (Total Rev, Gross Profit, Net Income)** | `summary_metrics` | `GET /api/v1/finance/reports` | `GET` |
| **Report Table (Income Statement)** | `report_data` | `GET /api/v1/finance/reports?type=income_statement` | `GET` |
| **Export Buttons (PDF/Excel)** | N/A | `GET /api/v1/finance/reports/export?format=pdf` | `GET` |
| **Generate Report Button** | N/A | Triggers report refresh | N/A |

## 3. Data Structure (API Contracts)

### A. Report Data (`GET /api/v1/finance/reports`)
**Request Parameters:**
- `type`: `income_statement`, `balance_sheet`, `cash_flow`
- `period_start`, `period_end`: ISO Dates
- `compare_with`: `previous_period`, `previous_year`, `budget`

**Response:**
```json
{
  "report_metadata": {
    "title": "Income Statement",
    "currency": "USD",
    "period_label": "Jan 1, 2023 - Oct 24, 2023 vs Previous Year"
  },
  "summary_metrics": {
    "total_revenue": 4250000.00,
    "revenue_change_pct": 12.5,
    "gross_profit": 1850000.00,
    "gross_profit_change_pct": 8.2,
    "net_income": 645000.00,
    "net_income_change_pct": -2.1
  },
  "report_data": [
    {
      "category": "Revenue",
      "items": [
        { "name": "Sales Revenue", "current": 3850000.00, "prior": 3400000.00, "variance": 450000.00, "pct_change": 13.2 },
        { "name": "Service Revenue", "current": 400000.00, "prior": 380000.00, "variance": 20000.00, "pct_change": 5.2 }
      ],
      "total": 4250000.00
    },
    {
      "category": "Cost of Goods Sold (COGS)",
      "items": [
        { "name": "Material Costs", "current": 1800000.00, "prior": 1600000.00, "variance": 200000.00, "pct_change": 12.5 },
        { "name": "Labor Costs", "current": 600000.00, "prior": 550000.00, "variance": 50000.00, "pct_change": 9.1 }
      ],
      "total": 2400000.00
    }
  ]
}
```

## 4. Logical Actions
- **Generate**: Hits the report API with current filters and updates the UI.
- **Toggle View**: Switch between table view and chart view (if implemented).
- **Export**: Opens a new tab or triggers a download for the generated report in chosen format.
- **Drill Down**: Clicking a line item category expands to show sub-items (Accrual basis).

## 5. Integration Notes
- Shares theme with Finance Dashboard.
- High emphasis on data precision and comparison indicators (Green/Red).
