# Page Specification: Dashboard Overview

## 1. Overview
The main landing page of the Apex ERP, providing a high-level summary of sales, financial status, and quick entry points.

## 2. UI Components & Data Mapping
| Component | UI Element | Data Keys / IDs | Associated API |
| :--- | :--- | :--- | :--- |
| **Sales Order Summary** | Card w/ Line Chart | `total_orders`, `new_orders`, `pending_orders`, `order_trend_values` | `GET /api/v1/dashboard/summary` |
| **Invoice Status** | Card w/ Donut Chart | `paid_count`, `unpaid_count`, `overdue_count` | `GET /api/v1/dashboard/invoice-stats` |
| **Quick Actions** | Button Group | `N/A` (Triggers navigation) | `N/A` |
| **Outstanding Payments** | Data Table | `invoice_id`, `customer_name`, `amount`, `due_date` | `GET /api/v1/payments/outstanding` |
| **Financial Performance**| Bar Chart | `month`, `revenue`, `expenses` | `GET /api/v1/dashboard/performance` |

## 3. Data Structure (API Contracts)

### A. Dashboard Summary (`GET /api/v1/dashboard/summary`)
```json
{
  "total_orders": 1250,
  "new_orders": 150,
  "pending_orders": 50,
  "order_trend_values": [70, 65, 50, 60, 40, 55, 20, 35, 10]
}
```

### B. Invoice Stats (`GET /api/v1/dashboard/invoice-stats`)
```json
{
  "paid_count": 950,
  "unpaid_count": 250,
  "overdue_count": 50
}
```

### C. Outstanding Payments (`GET /api/v1/payments/outstanding`)
```json
[
  {
    "invoice_id": "INV-2023-101",
    "customer_name": "Acme Corp",
    "amount": 5200.00,
    "due_date": "2023-10-28"
  },
  ...
]
```

## 4. Logical Actions
- **Click Create New Sales Order**: Redirects to `/views/sales_order_form.html`.
- **Click Create New Invoice**: Redirects to `/views/invoice_form.html`.
- **Table Row Click**: Navigates to the specific Invoice detail page.
