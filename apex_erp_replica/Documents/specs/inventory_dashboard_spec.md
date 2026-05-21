# Page Specification: Inventory Dashboard

## 1. Overview
The Inventory Dashboard provides a high-level overview of stock levels, values, and turnover rates. It also serves as a navigation hub for inventory-related tasks like stock adjustments and goods receipts.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Total Stock Value Card** | `total_value` | `GET /api/v1/inventory/summary` | `GET` |
| **Low Stock Items Card** | `low_stock_count` | `GET /api/v1/inventory/summary` | `GET` |
| **Inventory Turnover Card** | `turnover_rate` | `GET /api/v1/inventory/summary` | `GET` |
| **Product List Button** | `N/A` | Links to `/Pages/product_list.html` | `N/A` |
| **Stock Adjustment Button** | `N/A` | Links to `/Pages/stock_adjustment.html` | `N/A` |
| **Goods Receipt Button** | `N/A` | Links to `/Pages/goods_receipt.html` | `N/A` |
| **Warehouse Locations Button**| `N/A` | Links to `/Pages/warehouse_locations.html`| `N/A` |
| **Stock Movements Table** | `movements[]` (product_name, sku, type, quantity, date, warehouse) | `GET /api/v1/inventory/movements` | `GET` |

## 3. Data Structure (API Contracts)

### A. Inventory Summary (`GET /api/v1/inventory/summary`)
```json
{
  "total_value": 1250000.00,
  "low_stock_count": 12,
  "turnover_rate": 4.8,
  "currency": "USD"
}
```

### B. Recent Stock Movements (`GET /api/v1/inventory/movements`)
```json
{
  "movements": [
    {
      "product_name": "HD Wireless Mouse",
      "sku": "SKU-84321",
      "type": "IN",
      "quantity": 50,
      "date": "2023-10-29",
      "warehouse": "Main-WH"
    },
    {
      "product_name": "Mechanical Keyboard",
      "sku": "SKU-98765",
      "type": "OUT",
      "quantity": -15,
      "date": "2023-10-28",
      "warehouse": "Main-WH"
    },
    {
      "product_name": "27\" 4K Monitor",
      "sku": "SKU-12345",
      "type": "ADJUST",
      "quantity": -2,
      "date": "2023-10-28",
      "warehouse": "Warehouse B"
    }
  ]
}
```

## 4. Logical Actions
- **Metric Highlighting**: The "Low Stock Items" card should show a warning icon if count > 0.
- **Movement Type Tagging**:
    - `IN`: Green "IN" badge.
    - `OUT`: Red "OUT" badge.
    - `ADJUST`: Yellow "ADJUST" badge.
- **Navigation**: The sidebar must allow expanding the "Inventory" section to access sub-pages.

## 5. Integration Notes
- **Linked from Sidebar**: The "Inventory Dashboard" item in the sidebar should be the primary entry point.
- **Consistent UI**: Uses the standard Apex ERP card and table components.
