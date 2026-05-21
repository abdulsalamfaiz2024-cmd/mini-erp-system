# Page Specification: Finance Dashboard

## 1. Overview
The Finance Dashboard provides a high-level overview of the organization's financial health, including key metrics, recent transactions, and quick access to financial management tools.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Total Revenue Card** | `total_revenue`, `revenue_change_pct` | `GET /api/v1/finance/summary` | `GET` |
| **Total Expenses Card** | `total_expenses`, `expenses_change_pct` | `GET /api/v1/finance/summary` | `GET` |
| **Net Profit Card** | `net_profit`, `profit_change_pct` | `GET /api/v1/finance/summary` | `GET` |
| **Cash Flow Card** | `cash_flow`, `cash_flow_change_pct` | `GET /api/v1/finance/summary` | `GET` |
| **Recent Transactions Table** | `transactions[]` | `GET /api/v1/finance/transactions?limit=10` | `GET` |
| **Quick Actions Buttons** | N/A | Navigation links | N/A |

## 3. Data Structure (API Contracts)

### A. Finance Summary (`GET /api/v1/finance/summary`)
**Response:**
```json
{
  "total_revenue": 485000.00,
  "revenue_change_pct": 12.5,
  "total_expenses": 312000.00,
  "expenses_change_pct": 8.2,
  "net_profit": 173000.00,
  "profit_change_pct": 18.7,
  "cash_flow": 95000.00,
  "cash_flow_change_pct": 5.3,
  "period": "October 2023"
}
```

### B. Recent Transactions (`GET /api/v1/finance/transactions?limit=10`)
**Response:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN-2023-001",
      "date": "2023-10-29",
      "description": "Invoice Payment - Acme Corp",
      "type": "CREDIT",
      "amount": 15000.00,
      "account": "Accounts Receivable"
    },
    {
      "transaction_id": "TXN-2023-002",
      "date": "2023-10-28",
      "description": "Office Supplies Purchase",
      "type": "DEBIT",
      "amount": 450.00,
      "account": "Office Expenses"
    },
    {
      "transaction_id": "TXN-2023-003",
      "date": "2023-10-28",
      "description": "Utility Bill Payment",
      "type": "DEBIT",
      "amount": 1200.00,
      "account": "Utilities"
    }
  ]
}
```

## 4. Logical Actions
- **Metric Cards**: Display with color-coded change indicators (green for positive, red for negative).
- **Quick Actions**:
  - "Expenses List" → Navigates to `expenses_list.html`
  - "New Expense" → Navigates to `new_expense_form.html`
  - "Financial Reports" → Navigates to `financial_reports.html`
  - "Journal Entries" → Navigates to `journal_entries.html`
- **Transaction Type Badges**:
  - `CREDIT`: Green badge
  - `DEBIT`: Red badge
- **View All Transactions**: Navigates to `general_ledger.html`

## 5. Integration Notes
- Main dashboard for the Finance section.
- Uses collapsible sub-menu pattern matching Inventory Dashboard.
- Subpages: Expenses List, New Expense Form, Financial Reports, General Ledger, Journal Entries.
