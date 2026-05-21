# Page Specification: Product List

## 1. Overview
The Product List page displays a searchable, filterable table of all products in the inventory system. It provides quick access to product details, stock levels, and actions like editing or viewing individual products.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Search Input** | `q` (query string) | `GET /api/v1/products?q={query}` | `GET` |
| **Category Filter** | `category` | `GET /api/v1/products?category={id}` | `GET` |
| **Product Table** | `products[]` | `GET /api/v1/products` | `GET` |
| **Add Product Button** | N/A | Links to `/Pages/product_form.html` | N/A |
| **View Action** | `product_id` | Links to `/Pages/product_details.html?id={id}` | N/A |
| **Edit Action** | `product_id` | Links to `/Pages/product_form.html?id={id}` | N/A |
| **Pagination** | `page`, `per_page` | `GET /api/v1/products?page={n}` | `GET` |

## 3. Data Structure (API Contracts)

### A. Product List (`GET /api/v1/products`)
**Request Query Parameters:**
- `q` (optional): Search term
- `category` (optional): Category filter ID
- `page` (optional, default: 1): Page number
- `per_page` (optional, default: 10): Items per page

**Response:**
```json
{
  "products": [
    {
      "product_id": "PRD-001",
      "sku": "SKU-84321",
      "name": "HD Wireless Mouse",
      "category": "Electronics",
      "unit_price": 29.99,
      "stock_quantity": 150,
      "reorder_level": 20,
      "status": "In Stock"
    },
    {
      "product_id": "PRD-002",
      "sku": "SKU-98765",
      "name": "Mechanical Keyboard",
      "category": "Electronics",
      "unit_price": 89.99,
      "stock_quantity": 8,
      "reorder_level": 15,
      "status": "Low Stock"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 47
  }
}
```

### B. Categories List (`GET /api/v1/products/categories`)
```json
{
  "categories": [
    { "id": 1, "name": "Electronics" },
    { "id": 2, "name": "Office Supplies" },
    { "id": 3, "name": "Furniture" }
  ]
}
```

## 4. Logical Actions
- **Search**: Debounced search (300ms) filters table by product name or SKU.
- **Category Filter**: Dropdown selection triggers API call with `category` param.
- **Status Badges**:
  - `In Stock`: Green badge
  - `Low Stock`: Yellow/Orange badge
  - `Out of Stock`: Red badge
- **View Button**: Navigates to `product_details.html?id={product_id}`.
- **Edit Button**: Navigates to `product_form.html?id={product_id}`.
- **Add Product**: Navigates to `product_form.html` (new product mode).

## 5. Integration Notes
- Linked from Inventory Dashboard sidebar as "Product List".
- Uses standard Apex ERP table styling from `main.css`.
