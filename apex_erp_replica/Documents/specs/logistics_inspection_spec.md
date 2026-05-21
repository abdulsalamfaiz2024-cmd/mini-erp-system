# Page Specification: Return Logistics & Inspection

## 1. Overview
The Logistics & Inspection page is designed for warehouse staff to verify the condition of returned goods. It facilitates the grading of items and determines their final disposition (restock, salvage, or RTV).

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Returns Checklist** | `checklist_items[]` | `GET /api/v1/returns/{id}/checklist` | `GET` |
| **Item Condition Radio**| `condition_code` | Part of PATCH payload | N/A |
| **Disposition Select** | `disposition_code` | Part of PATCH payload | N/A |
| **Verify Serial #** | `serial_number_scanned`| Part of PATCH payload | N/A |
| **Inspection Queue** | `queue_items[]` | `GET /api/v1/returns/{id}` | `GET` |
| **Complete Inspection** | Request Body | `PATCH /api/v1/returns/{id}/inspect` | `PATCH` |

## 3. Data Structure (API Contracts)

### A. Inspection Data (`GET /api/v1/returns/RET-2024-001/inspect`)
**Response:**
```json
{
  "return_id": "RET-2024-001",
  "items": [
    {
      "line_id": 101,
      "sku": "SKU-KB-001",
      "name": "Mechanical Keyboard RTX",
      "expected_qty": 1,
      "checklist": ["Original Box included", "Accessories present", "No physical damage"]
    }
  ],
  "disposition_options": ["Restock", "Salvage/Parts", "RTV (Return to Vendor)", "Refurbish"]
}
```

### B. Submit Inspection Result (`PATCH /api/v1/returns/RET-2024-001/inspect`)
**Request:**
```json
{
  "line_results": [
    {
      "line_id": 101,
      "received_qty": 1,
      "condition": "used",
      "disposition": "restock",
      "notes": "Light scratches on back",
      "checks": { "box": true, "accessories": true, "damage": false }
    }
  ]
}
```

## 4. Logical Actions
- **Condition Grading**: Impacts the refundable amount calculation (conceptual).
- **Serial Validation**: If item is serialized, prevents completion until a valid serial is entered or "No Serial" is checked.
- **Restock Action**: If 'Restock' is chosen, the system prepares to increment inventory levels once approved.

## 5. Integration Notes
- High focus on mobile-friendly inputs for warehouse staff (large buttons, radio groups).
- Sidebar shows the inspection queue for the current return request.
