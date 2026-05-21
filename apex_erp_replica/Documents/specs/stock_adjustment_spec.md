# Page Specification: Stock Adjustment Form

## 1. Overview
The Stock Adjustment Form allows users to manually adjust inventory quantities for products. This is used for corrections, damaged goods, cycle counts, or other inventory discrepancies.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Adjustment ID** | `adjustment_id` (auto-generated) | `GET /api/v1/inventory/adjustments/next-id` | `GET` |
| **Adjustment Date** | `adjustment_date` | N/A (form input) | N/A |
| **Warehouse Dropdown** | `warehouse_id` | `GET /api/v1/warehouses` | `GET` |
| **Reason Dropdown** | `reason` | Static list | N/A |
| **Product Search** | `product_id`, `sku` | `GET /api/v1/products?q={query}` | `GET` |
| **Current Qty** | `current_qty` | `GET /api/v1/products/{id}/stock` | `GET` |
| **Adjustment Qty** | `adjustment_qty` | N/A (form input) | N/A |
| **New Qty** | `new_qty` (calculated) | N/A | N/A |
| **Notes** | `notes` | N/A (form input) | N/A |
| **Submit Button** | Full payload | `POST /api/v1/inventory/adjustments` | `POST` |
| **Cancel Button** | N/A | Navigates back | N/A |

## 3. Data Structure (API Contracts)

### A. Submit Adjustment (`POST /api/v1/inventory/adjustments`)
**Request:**
```json
{
  "adjustment_id": "ADJ-2023-001",
  "adjustment_date": "2023-10-29",
  "warehouse_id": "WH-001",
  "reason": "Damaged Goods",
  "line_items": [
    {
      "product_id": "PRD-001",
      "sku": "SKU-84321",
      "current_qty": 150,
      "adjustment_qty": -5,
      "new_qty": 145
    },
    {
      "product_id": "PRD-002",
      "sku": "SKU-98765",
      "current_qty": 8,
      "adjustment_qty": 2,
      "new_qty": 10
    }
  ],
  "notes": "Cycle count correction for Q4 audit",
  "created_by": "user_id"
}
```

**Response:**
```json
{
  "success": true,
  "adjustment_id": "ADJ-2023-001",
  "message": "Stock adjustment recorded successfully"
}
```

### B. Warehouses List (`GET /api/v1/warehouses`)
```json
{
  "warehouses": [
    { "id": "WH-001", "name": "Main Warehouse" },
    { "id": "WH-002", "name": "Warehouse B" },
    { "id": "WH-003", "name": "Warehouse C" }
  ]
}
```

### C. Adjustment Reasons (Static)
```json
{
  "reasons": [
    "Damaged Goods",
    "Cycle Count",
    "Theft/Loss",
    "Return to Vendor",
    "Found Stock",
    "Other"
  ]
}
```

## 4. Logical Actions
- **Auto-calculate New Qty**: `new_qty = current_qty + adjustment_qty`
- **Positive/Negative Qty**: Positive = stock increase, Negative = stock decrease
- **Add Line Item**: Click "+ Add Line" to add another product row.
- **Remove Line Item**: Click "×" to remove a row.
- **Validation**: Ensure product is selected, adjustment_qty is not 0, warehouse is selected.
- **Submit**: Sends POST to API, then redirects to `inventory_dashboard.html`.
- **Cancel**: Navigates back to previous page.

## 5. Integration Notes
- Linked from Inventory Dashboard sidebar as "Stock Adjustment".
- Uses form grid layout from `main.css`.
