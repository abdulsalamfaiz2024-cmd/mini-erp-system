# Purchase Order List Technical Specification

## A. UI-to-API Mapping Table

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| Search Bar | `query` | `/api/purchasing/pos` | GET |
| Status Filter | `status` | `/api/purchasing/pos` | GET |
| Date Range Filter | `date_range` | `/api/purchasing/pos` | GET |
| PO Table | `purchase_orders`, `total_count` | `/api/purchasing/pos` | GET |

## B. API Data Contract

### GET `/api/purchasing/pos`
**Query Parameters:** `query`, `status`, `date_range`, `page`, `limit`
**Response:**
```json
{
  "purchase_orders": [
    {
      "po_id": "PO-2024-00781",
      "date": "2023-10-26",
      "supplier": "Global Tech Imports",
      "total_amount": 15250.00,
      "status": "Approved"
    },
    {
      "po_id": "PO-2024-00780",
      "date": "2023-10-25",
      "supplier": "Office Supply Co.",
      "total_amount": 875.50,
      "status": "Shipped"
    }
  ],
  "total_count": 150
}
```

## C. Logic & Actions
- **Create New PO Button**: Navigates to `/Pages/new_purchase_order_form.html`.
- **Search/Filter**: Triggers a re-fetch of the PO list with updated parameters.
- **PO Number Link**: Navigates to `/Pages/purchase_order_details.html?id={po_id}`.
- **Row Action (...)**: Opens dropdown with options (Edit, View, Delete, Print).
- **Pagination**: Navigates through the paginated list of purchase orders.
