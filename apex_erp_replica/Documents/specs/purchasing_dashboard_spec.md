# Purchasing Dashboard Technical Specification

## A. UI-to-API Mapping Table

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| Metric: Pending Approval | `pending_approval_count`, `pending_approval_trend` | `/api/purchasing/dashboard/metrics` | GET |
| Metric: To Be Received | `to_be_received_count`, `to_be_received_trend` | `/api/purchasing/dashboard/metrics` | GET |
| Metric: Overdue | `overdue_count`, `overdue_trend` | `/api/purchasing/dashboard/metrics` | GET |
| Metric: Monthly Spend | `monthly_spend_amount`, `monthly_spend_trend` | `/api/purchasing/dashboard/metrics` | GET |
| Chart: Spend vs. Budget | `spend_data`, `budget_limit` | `/api/purchasing/dashboard/spend-vs-budget` | GET |
| Chart: POs by Status | `status_distribution` | `/api/purchasing/dashboard/po-status` | GET |
| Table: Recent Purchase Orders | `recent_pos` | `/api/purchasing/dashboard/recent-pos` | GET |

## B. API Data Contract

### GET `/api/purchasing/dashboard/metrics`
**Response:**
```json
{
  "pending_approval_count": 12,
  "pending_approval_trend": "+2%",
  "to_be_received_count": 8,
  "to_be_received_trend": "-5%",
  "overdue_count": 3,
  "overdue_trend": "+1%",
  "monthly_spend_amount": 12450.78,
  "monthly_spend_trend": "-10%"
}
```

### GET `/api/purchasing/dashboard/recent-pos`
**Response:**
```json
{
  "recent_pos": [
    {
      "po_number": "PO-00875",
      "supplier": "Global Tech Inc.",
      "status": "Approved",
      "date": "2024-03-12",
      "amount": 2500.00
    },
    {
      "po_number": "PO-00874",
      "supplier": "Office Supplies Co.",
      "status": "Shipped",
      "date": "2024-03-11",
      "amount": 450.50
    }
  ]
}
```

## C. Logic & Actions
- **New Purchase Order Button**: Navigates to `/Pages/new_purchase_order_form.html`.
- **View Purchase Orders Button**: Navigates to `/Pages/purchase_order_list.html`.
- **Manage Suppliers Button**: Navigates to `/Pages/suppliers_list.html`.
- **PO Row Click**: Navigates to `/Pages/purchase_order_details.html?id={po_number}`.
