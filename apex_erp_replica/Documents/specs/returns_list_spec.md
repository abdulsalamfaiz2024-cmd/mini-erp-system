# Page Specification: Returns List

## 1. Overview
The Returns List page allows staff to view, filter, and manage all product return requests in the system. It provide a central grid for tracking the lifecycle of a return from initial request to final credit processing or restock.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Search Bar** | `query` | `GET /api/v1/returns?q={query}` | `GET` |
| **Status Filter** | `status` | `GET /api/v1/returns?status={status}` | `GET` |
| **Date Range Filter** | `start_date`, `end_date` | `GET /api/v1/returns?from={date}&to={date}` | `GET` |
| **Returns Table** | `returns_list[]` | `GET /api/v1/returns` | `GET` |
| **Pagination** | `current_page`, `total_pages` | `GET /api/v1/returns` | `GET` |
| **Action: View** | `return_id` | Navigation to `return_details.html` | N/A |

## 3. Data Structure (API Contracts)

### A. Returns List Fetch (`GET /api/v1/returns`)
**Response:**
```json
{
  "returns_list": [
    {
      "return_id": "RET-2024-001",
      "order_id": "SO-875",
      "customer": "Global Tech Inc.",
      "date": "2024-03-20",
      "items_count": 3,
      "reason": "Defective",
      "status": "pending",
      "resolution": "Refund"
    },
    {
      "return_id": "RET-2024-002",
      "order_id": "SO-872",
      "customer": "Office Supplies Co.",
      "date": "2024-03-19",
      "items_count": 1,
      "reason": "Wrong Item",
      "status": "authorized",
      "resolution": "Replacement"
    }
  ],
  "pagination": {
    "current": 1,
    "total": 15,
    "per_page": 20
  }
}
```

## 4. Logical Actions
- **Filter Apply**: Refreshing the grid data based on selected filters (Status, Date, Reason).
- **Export CSV**: Triggers a backend generate and download of the current filtered list.
- **Status Badges**:
  - `pending`: Orange text/bg
  - `authorized`: Green text/bg
  - `inspected`: Blue text/bg
  - `completed`: Gray text/bg
  - `rejected`: Red text/bg

## 5. Integration Notes
- Shares data grid styling with Product List and Sales Orders.
- Linked to `return_details.html` via clicking on the Return ID or the View button.
