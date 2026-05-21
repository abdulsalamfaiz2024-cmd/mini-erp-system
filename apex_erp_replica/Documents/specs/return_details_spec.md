# Page Specification: Return Details

## 1. Overview
The Return Details page is the central management hub for a single return request. It tracks the progress from authorization through inspection to final resolution.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Status Header** | `current_status` | `GET /api/v1/returns/{id}` | `GET` |
| **Items Table** | `items[]` | `GET /api/v1/returns/{id}` | `GET` |
| **Inspection Log** | `inspection_history[]` | `GET /api/v1/returns/{id}/inspection` | `GET` |
| **Activity History** | `activities[]` | `GET /api/v1/returns/{id}/history` | `GET` |
| **Action: Authorize** | N/A | `PATCH /api/v1/returns/{id}/authorize` | `PATCH` |
| **Action: Reject** | `rejection_reason` | `PATCH /api/v1/returns/{id}/reject` | `PATCH` |
| **Sidebar Info** | `customer`, `logistics` | `GET /api/v1/returns/{id}` | `GET` |

## 3. Data Structure (API Contracts)

### A. Return Details (`GET /api/v1/returns/RET-2024-001`)
**Response:**
```json
{
  "return_id": "RET-2024-001",
  "status": "pending_inspection",
  "authorized_at": "2024-03-21T10:00:00Z",
  "customer": {
    "name": "Global Tech Inc.",
    "contact": "John Doe",
    "email": "j.doe@globaltech.com"
  },
  "logistics": {
    "tracking_number": "UPS-123456789",
    "carrier": "UPS",
    "expected_arrival": "2024-03-25"
  },
  "items": [
    {
      "sku": "SKU-KB-001",
      "name": "Mechanical Keyboard",
      "qty": 1,
      "condition": "uninspected"
    }
  ],
  "activities": [
    { "date": "2024-03-20 14:00", "user": "System", "msg": "Return initiated by customer" },
    { "date": "2024-03-21 10:00", "user": "Alice Manager", "msg": "Return authorized" }
  ]
}
```

## 4. Logical Actions
- **Authorize Return**: Changes status and generates a return label (conceptual).
- **Process Refund Button**: Linked only if inspection is complete and resolution is 'Refund'. Navigates to `credit_processing.html`.
- **Inspection Link**: Navigates to `logistics_inspection.html` for warehouse staff.

## 5. Integration Notes
- Sidebar contains contextual actions like "Print Label" or "Track Shipment".
- Status timeline shows chronological progress of the request.
