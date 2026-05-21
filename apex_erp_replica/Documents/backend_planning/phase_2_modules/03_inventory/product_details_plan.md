# Non-Blind Implementation Plan: Product Details

## 1. UI Infrastructure Analysis
*Reference File: `Pages/product_details.html`*

The Product Details page is a deep-dive view into a specific SKU. The following HTML structures must be targeted:

### 1.1. Product Header
- **Breadcrumbs**: `.breadcrumbs` (Line 205). (Should update last segment with product name).
- **Product Title**: `.product-title` (Line 228).
- **Status Badge**: `.status-badge` (Line 229).
- **Meta Info**: `.product-sku` (Line 231). (SKU and Barcode).

### 1.2. Info & Pricing
- **Description**: (Lines 232-236).
- **Info Grid**: (Lines 237-254).
    - Category, Brand, Unit Price, Cost Price.

### 1.3. Stock Distribution
- **Stock Card Grid**: (Lines 267-284).
    - Card 1: Total Stock. (Highlighting logic in Line 268).
    - Card 2-4: Individual Warehouse quantities.
- **Stock Alert**: (Line 286). (Warns if `total_stock < reorder_level`).

### 1.4. Transaction Ledger
- **Table Body**: `.data-table tbody` (Line 310).
- **Column Mapping**:
    - `Date`: Col 1.
    - `Type`: Col 2 (Badge style: `in|out|adjust`).
    - `Quantity`: Col 3 (Colored text).
    - `Reference`: Col 4 (Linked to doc: `GR|SO|ADJ`).
    - `Warehouse`: Col 5.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/product_details_spec.md`*

| Spec Key | API JSON Path | Target UI Element |
| :--- | :--- | :--- |
| `product_id` | `root.product_id` | Used to fetch secondary API calls |
| `unit_price`| `root.unit_price` | Info Item (Green col) |
| `warehouse_stock[]` | `warehouse_stock`| Populate Stock Cards |
| `reference` | `transactions[].reference` | Table Column 4 (Anchor Tag) |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Composite Data Retrieval
The product detail view requires data from multiple tables.
1. `GET /api/v1/products/{id}`:
    - Primary fetch from `inv_products`.
2. `GET /api/v1/products/{id}/stock`:
    - Join `inv_stock` with `mst_warehouses`.
    - Group by warehouse to sum quantities for this product.
3. `GET /api/v1/products/{id}/transactions`:
    - Query `inv_stock_movements` for this product.
    - Limit to top 10 most recent.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/product_details.js`*

1. **Stock Alert Logic**:
```javascript
function updateStockAlert(total, reorder) {
    const alertBox = document.querySelector('.stock-alert');
    if (total < reorder) {
        alertBox.innerHTML = `⚠️ <strong>Low Stock:</strong> Below ${reorder} units!`;
        alertBox.className = 'stock-alert warning';
    } else {
        alertBox.innerHTML = `✅ Stock level is healthy (${total} > ${reorder})`;
    }
}
```
2. **Dynamic Stock Cards**:
```javascript
function renderStockCards(stockData) {
    const container = document.querySelector('.stock-cards-grid');
    // Clear and inject cards based on warehouse_stock array...
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/product_details.html`. Ensure "Quantity" in the table uses `+` for `IN` and `-` for `OUT`.
2. [ ] **Cross-Linking**: Verify that the "Reference" link in the transaction table correctly routes based on type (e.g., if ref starts with `SO-`, route to `sales_order_details.html?id=...`).
3. [ ] **Precision**: Cost price and profit margin should be calculated and displayed to 2 decimal places.
