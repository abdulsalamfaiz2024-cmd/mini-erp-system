# Page Specification: General Ledger Overview

## 1. Overview
The General Ledger Overview allows finance managers to view the current standing of all accounts. It summarizes assets, liabilities, equity, revenue, and expenses in one central view, with the ability to drill down into specific account activities.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Search Accounts** | `q` | `GET /api/v1/finance/ledger/accounts?q={query}` | `GET` |
| **Fiscal Year Filter** | `fiscal_year` | `GET /api/v1/finance/ledger/summary` | `GET` |
| **Total Assets Card** | `total_assets`, `assets_change` | `GET /api/v1/finance/ledger/summary` | `GET` |
| **Total Liabilities Card** | `total_liabilities`, `liabilities_change` | `GET /api/v1/finance/ledger/summary` | `GET` |
| **Total Equity Card** | `total_equity`, `equity_change` | `GET /api/v1/finance/ledger/summary` | `GET` |
| **Account Table** | `accounts[]` | `GET /api/v1/finance/ledger/accounts` | `GET` |
| **View Account Details** | `account_id` | `GET /api/v1/finance/ledger/accounts/{id}/activity` | `GET` |
| **Export Data** | N/A | `GET /api/v1/finance/ledger/export` | `GET` |

## 3. Data Structure (API Contracts)

### A. Ledger Summary (`GET /api/v1/finance/ledger/summary`)
**Response:**
```json
{
  "fiscal_year": "2024",
  "quarter": "Q3",
  "period": "Period 9",
  "summary": {
    "total_assets": 1250000.00,
    "assets_change_pct": 12.0,
    "total_liabilities": 450000.00,
    "liabilities_change_pct": -5.0,
    "total_equity": 800000.00,
    "equity_change_pct": 8.0,
    "revenue_ytd": 3200000.00,
    "revenue_change_pct": 15.0,
    "expenses_ytd": 2100000.00,
    "expenses_change_pct": 10.0
  }
}
```

### B. Accounts List (`GET /api/v1/finance/ledger/accounts`)
**Response:**
```json
{
  "accounts": [
    {
      "code": "101-000",
      "name": "Cash on Hand",
      "category": "Asset",
      "debit": 25400.00,
      "credit": 0.00,
      "balance": 25400.00,
      "status": "Active"
    },
    {
      "code": "201-000",
      "name": "Accounts Payable",
      "category": "Liability",
      "debit": 5000.00,
      "credit": 45200.00,
      "balance": -40200.00,
      "status": "Active"
    },
    {
      "code": "501-200",
      "name": "Rent Expense",
      "category": "Expense",
      "debit": 12500.00,
      "credit": 0.00,
      "balance": -12500.00,
      "status": "Active"
    }
  ],
  "pagination": { "current": 1, "total": 145 }
}
```

## 4. Logical Actions
- **Export Ledger**: Triggers a CSV/Excel download of the full Chart of Accounts with current balances.
- **Drill Down**: Clicking the "View" (eye icon) navigates to a detailed transaction list for that account (conceptualized as `Pages/account_details.html`).
- **Tab Switching**: Users can toggle between "Overview", "Journal Entries", "Chart of Accounts", and "Reports".

## 5. Integration Notes
- Central hub for financial accounting data.
- Color coding for categories: Blue for Assets, Orange for Liabilities, Purple for Equity, Green for Revenue, Red for Expenses.
- Balance calculation logic: Assets = Liabilities + Equity.
