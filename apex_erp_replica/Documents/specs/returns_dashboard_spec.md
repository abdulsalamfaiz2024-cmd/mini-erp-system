# Page Specification: Returns Dashboard

## 1. Overview
The Returns Dashboard provides a high-level summary of reverse logistics performance, helping managers monitor return rates, processing times, and financial impacts of product returns. It serves as the entry point for initiating new return requests and managing the returns workflow.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **KPI: Pending Returns** | `pending_count` | `GET /api/v1/returns/summary` | `GET` |
| **KPI: Refund Value** | `refund_total_value` | `GET /api/v1/returns/summary` | `GET` |
| **KPI: Avg. Process Time** | `avg_processing_days` | `GET /api/v1/returns/summary` | `GET` |
| **KPI: Return Rate** | `return_rate_percentage` | `GET /api/v1/returns/summary` | `GET` |
| **Chart: Return Volume Trend** | `trend_data[]` | `GET /api/v1/returns/analytics/trend` | `GET` |
| **Chart: Return Reasons** | `reasons_breakdown[]` | `GET /api/v1/returns/analytics/reasons` | `GET` |
| **Recent Return Requests Table** | `recent_returns[]` | `GET /api/v1/returns/recent` | `GET` |
| **Create Return Button** | N/A | Navigation to `new_return_request.html` | N/A |

## 3. Data Structure (API Contracts)

### A. Returns Summary (`GET /api/v1/returns/summary`)
**Response:**
```json
{
  "pending_count": 42,
  "pending_trend": "+12%",
  "refund_total_value": 12500.50,
  "refund_trend": "-5%",
  "avg_processing_days": 3.2,
  "avg_processing_trend": "+0.5",
  "return_rate_percentage": 4.5,
  "return_rate_trend": "-0.2%"
}
```

### B. Recent Returns (`GET /api/v1/returns/recent`)
**Response:**
```json
{
  "recent_returns": [
    {
      "return_id": "RET-2024-001",
      "customer_name": "Global Tech Inc.",
      "customer_avatar": "https://i.pravatar.cc/100?u=1",
      "date": "2024-03-20",
      "reason": "Defective",
      "status": "pending"
    },
    {
      "return_id": "RET-2024-002",
      "customer_name": "Office Supplies Co.",
      "customer_avatar": "https://i.pravatar.cc/100?u=2",
      "date": "2024-03-19",
      "reason": "Wrong Item",
      "status": "authorized"
    }
  ]
}
```

## 4. Logical Actions
- **Initiate Return**: Clicking the "Create Return Request" button navigates to the request form.
- **View Details**: Clicking "View" on a table row navigates to the unified return details page.
- **Drill Down**: Clicking on chart segments filters the returns list (conceptual for future).

## 5. Integration Notes
- Uses standard metric card components from `main.css`.
- Progress bars in the "Reasons" chart are styled using CSS variables for consistency.
- Status badges follow the enterprise color palette: `pending` (Yellow), `authorized` (Green), `rejected` (Red).
