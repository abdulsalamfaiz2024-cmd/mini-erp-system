# Page Specification: Goods Receipt Form

## 1. Overview
The Goods Receipt Form records the arrival of goods into the warehouse. It links to Purchase Orders and updates inventory quantities upon confirmation.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Receipt ID** | `receipt_id` (auto-generated) | `GET /api/v1/inventory/receipts/next-id` | `GET` |
| **Receipt Date** | `receipt_date` | N/A (form input) | N/A |
| **Supplier Dropdown** | `supplier_id` | `GET /api/v1/suppliers` | `GET` |
| **Purchase Order Link** | `po_id` | `GET /api/v1/purchase-orders?supplier={id}` | `GET` |
| **Warehouse Dropdown** | `warehouse_id` | `GET /api/v1/warehouses` | `GET` |
| **Line Items Table** | `line_items[]` | From linked PO | N/A |
| **Received Qty** | `received_qty` | N/A (form input) | N/A |
| **Submit Button** | Full payload | `POST /api/v1/inventory/receipts` | `POST` |
| **Cancel Button** | N/A | Navigates back | N/A |

## 3. Data Structure (API Contracts)

### A. Submit Goods Receipt (`POST /api/v1/inventory/receipts`)
**Request:**
```json
{
  "receipt_id": "GR-2023-001",
  "receipt_date": "2023-10-29",
  "supplier_id": "SUP-001",
  "supplier_name": "Tech Distributors Inc.",
  "po_id": "PO-2023-045",
  "warehouse_id": "WH-001",
  "line_items": [
    {
      "product_id": "PRD-001",
      "sku": "SKU-84321",
      "product_name": "HD Wireless Mouse",
      "ordered_qty": 100,
      "received_qty": 100,
      "unit_price": 15.00
    },
    {
      "product_id": "PRD-002",
      "sku": "SKU-98765",
      "product_name": "Mechanical Keyboard",
      "ordered_qty": 50,
      "received_qty": 48,
      "unit_price": 45.00
    }
  ],
  "notes": "2 keyboards missing from shipment",
  "received_by": "user_id"
}
```

**Response:**
```json
{
  "success": true,
  "receipt_id": "GR-2023-001",
  "message": "Goods receipt recorded successfully. Inventory updated."
}
```

### B. Suppliers List (`GET /api/v1/suppliers`)
```json
{
  "suppliers": [
    { "id": "SUP-001", "name": "Tech Distributors Inc." },
    { "id": "SUP-002", "name": "Office Pro Supplies" },
    { "id": "SUP-003", "name": "Global Electronics" }
  ]
}
```

### C. Purchase Orders by Supplier (`GET /api/v1/purchase-orders?supplier={id}&status=pending`)
```json
{
  "purchase_orders": [
    { "po_id": "PO-2023-045", "date": "2023-10-20", "total": "$2,750.00" },
    { "po_id": "PO-2023-038", "date": "2023-10-15", "total": "$1,200.00" }
  ]
}
```

## 4. Logical Actions
- **Supplier Selection**: Triggers fetch of open POs for that supplier.
- **PO Selection**: Auto-populates line items from the selected PO.
- **Received Qty Validation**: Cannot exceed ordered qty (warning only).
- **Discrepancy Note**: If received ≠ ordered, prompt for notes.
- **Submit**: Sends POST, updates inventory, closes/partially closes PO.
- **Cancel**: Navigates back without saving.

## 5. Integration Notes
- Linked from Inventory Dashboard sidebar as "Goods Receipt".
- Uses form grid layout from `main.css`.
