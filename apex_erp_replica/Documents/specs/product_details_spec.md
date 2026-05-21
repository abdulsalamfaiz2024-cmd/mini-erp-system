# Page Specification: Product Details

## 1. Overview
The Product Details page displays comprehensive information about a single product, including its specifications, stock levels across warehouses, pricing history, and recent transactions.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Product Header** | `product_id`, `name`, `sku`, `status` | `GET /api/v1/products/{id}` | `GET` |
| **Product Image** | `image_url` | `GET /api/v1/products/{id}` | `GET` |
| **Basic Info Card** | `category`, `unit_price`, `cost_price`, `barcode` | `GET /api/v1/products/{id}` | `GET` |
| **Stock by Warehouse** | `warehouse_stock[]` | `GET /api/v1/products/{id}/stock` | `GET` |
| **Transaction History** | `transactions[]` | `GET /api/v1/products/{id}/transactions` | `GET` |
| **Edit Button** | N/A | Links to `/Pages/product_form.html?id={id}` | N/A |
| **Back Button** | N/A | Navigates to `product_list.html` | N/A |

## 3. Data Structure (API Contracts)

### A. Product Details (`GET /api/v1/products/{id}`)
**Response:**
```json
{
  "product_id": "PRD-001",
  "sku": "SKU-84321",
  "name": "HD Wireless Mouse",
  "description": "High-definition wireless optical mouse with ergonomic design. Features adjustable DPI settings and long battery life.",
  "category": "Electronics",
  "subcategory": "Computer Peripherals",
  "brand": "TechPro",
  "unit_price": 29.99,
  "cost_price": 15.00,
  "profit_margin": 49.98,
  "barcode": "7891234567890",
  "weight": "0.15 kg",
  "dimensions": "10 x 6 x 4 cm",
  "reorder_level": 20,
  "status": "Active",
  "image_url": "/assets/images/products/mouse.png",
  "created_at": "2023-01-15",
  "updated_at": "2023-10-28"
}
```

### B. Stock by Warehouse (`GET /api/v1/products/{id}/stock`)
```json
{
  "total_stock": 350,
  "warehouse_stock": [
    { "warehouse_id": "WH-001", "name": "Main Warehouse", "quantity": 150, "zone": "Zone A" },
    { "warehouse_id": "WH-002", "name": "Warehouse B", "quantity": 120, "zone": "Zone B" },
    { "warehouse_id": "WH-003", "name": "Warehouse C", "quantity": 80, "zone": "Zone A" }
  ]
}
```

### C. Transaction History (`GET /api/v1/products/{id}/transactions?limit=10`)
```json
{
  "transactions": [
    {
      "transaction_id": "TXN-001",
      "type": "IN",
      "quantity": 50,
      "date": "2023-10-29",
      "reference": "GR-2023-001",
      "warehouse": "Main Warehouse"
    },
    {
      "transaction_id": "TXN-002",
      "type": "OUT",
      "quantity": -15,
      "date": "2023-10-28",
      "reference": "SO-2023-089",
      "warehouse": "Main Warehouse"
    },
    {
      "transaction_id": "TXN-003",
      "type": "ADJUST",
      "quantity": -2,
      "date": "2023-10-27",
      "reference": "ADJ-2023-005",
      "warehouse": "Warehouse B"
    }
  ]
}
```

## 4. Logical Actions
- **Edit Product**: Navigates to `product_form.html?id={product_id}`.
- **Back to List**: Navigates to `product_list.html`.
- **Transaction Type Badges**:
  - `IN`: Green badge
  - `OUT`: Red badge
  - `ADJUST`: Yellow badge
- **Stock Alert**: If total_stock < reorder_level, show warning indicator.
- **View Reference**: Clicking reference links to corresponding document (GR, SO, ADJ).

## 5. Integration Notes
- Accessed from Product List via "View" action.
- Uses detail grid and card layouts from `main.css`.
