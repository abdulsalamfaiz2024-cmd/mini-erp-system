# Page Specification: New Return Request

## 1. Overview
The New Return Request form is a wizard-style interface for capturing return details from customers. It handles order lookups, item selection with quantity validation, and reason categorization.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Order Search Input** | `order_number` | `GET /api/v1/orders/lookup/{id}` | `GET` |
| **Customer Info Box** | `customer_name` | `GET /api/v1/orders/lookup/{id}` | `GET` |
| **Item Selection Table**| `order_items[]` | `GET /api/v1/orders/lookup/{id}` | `GET` |
| **Return Qty Input** | `return_qty` | Part of POST payload | N/A |
| **Reason Dropdown** | `reason_code` | `GET /api/v1/returns/reasons` | `GET` |
| **Resolution Selection**| `desired_resolution` | `GET /api/v1/returns/resolutions` | `GET` |
| **Internal Notes** | `internal_notes` | Part of POST payload | N/A |
| **Create Request Button**| Request Body | `POST /api/v1/returns` | `POST` |

## 3. Data Structure (API Contracts)

### A. Order Lookup (`GET /api/v1/orders/lookup/SO-875`)
**Response:**
```json
{
  "order_id": "SO-875",
  "customer_id": "CUST-001",
  "customer_name": "Acme Corp",
  "order_date": "2024-03-10",
  "status": "Delivered",
  "total_value": 1250.00,
  "items": [
    {
      "sku": "SKU-KB-001",
      "name": "Mechanical Keyboard RTX",
      "description": "Blue Switches",
      "sold_qty": 2,
      "unit_price": 89.99
    },
    {
      "sku": "SKU-MS-005",
      "name": "Wireless Gaming Mouse",
      "description": "16000 DPI",
      "sold_qty": 1,
      "unit_price": 59.99
    }
  ]
}
```

### B. Create Return (`POST /api/v1/returns`)
**Request:**
```json
{
  "order_id": "SO-875",
  "items": [
    { "sku": "SKU-KB-001", "qty": 1 }
  ],
  "reason": "defective",
  "resolution": "refund",
  "notes": "Left shift key sticking."
}
```

## 4. Logical Actions
- **Fetch Items**: Validates the order number and populates the item selection table.
- **Quantity Validation**: Ensures Return Qty is > 0 and <= Sold Qty.
- **Cancel**: Returns user to the Returns List without saving.

## 5. Integration Notes
- Sidebar displays a "Order Context" summary once a valid order is fetched.
- Uses multi-step form progress indicators (Step 1, 2, 3).
