# Non-Blind Implementation Plan: Product List

## 1. UI Infrastructure Analysis
*Reference File: `Pages/product_list.html`*

The Product List is the primary inventory catalog. The following HTML structures must be targeted:

### 1.1. Catalog Header
- **Main Heading**: `.page-title` (Line 127).
- **Add Product Action**: `.btn.btn-blue` (Line 128). Targets `product_form.html`.

### 1.2. Filtering Controls
- **Global Search**: `.search-input-wrapper input` (Line 138).
- **Category Filter**: `select` (Line 140). (Populated from server).

### 1.3. Catalog Table
- **Table Body**: `.data-table tbody` (Line 164).
- **Row Columns**:
    - `SKU`: Col 1.
    - `Product Name`: Col 2 (font-weight: 600).
    - `Category`: Col 3.
    - `Unit Price`: Col 4.
    - `Stock Qty`: Col 5.
    - `Reorder Level`: Col 6.
    - `Status`: Col 7 (containing `.status-badge` with class `approved|pending|overdue`).
    - `Actions`: Col 8 (containing `.action-links` spans).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/product_list_spec.md`*

| Spec Key | API JSON Path | Functional UI Logic |
| :--- | :--- | :--- |
| `products[]` | `products` | `.data-table tbody` rows |
| `status` | `products[].status` | Map text (In Stock) to class (approved) |
| `reorder_level` | `products[].reorder_level`| If `stock_qty < level` -> Set status to Low Stock |
| `product_id` | `products[].product_id` | Attached to View link: `?id={val}` |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Catalog Query
1. `GET /api/v1/products`:
    - `SELECT * FROM inv_products`.
    - Join `mst_categories`.
    - Apply pagination (Offset/Limit) and text search on `name` or `sku`.
2. `GET /api/v1/products/categories`:
    - Distinct categories for the filter dropdown.

### 3.2. Status Compute Logic
The backend should calculate the `status` field on-the-fly:
- `if stock_qty <= 0: return 'Out of Stock'`
- `if stock_qty <= reorder_level: return 'Low Stock'`
- `else: return 'In Stock'`

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/product_list.js`*

1. **Status CSS Mapper**:
```javascript
function getStatusClass(status) {
    const map = { 'In Stock': 'approved', 'Low Stock': 'pending', 'Out of Stock': 'overdue' };
    return map[status] || 'default';
}
```
2. **Search Debounce**:
```javascript
let timer;
searchInput.oninput = () => {
    clearTimeout(timer);
    timer = setTimeout(() => refreshTable(this.value), 300);
};
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/product_list.html`. Ensure the View link targets `product_details.html?id=[product_id]`.
2. [ ] **Stock Sorting**: Verify that sorting by "Stock Qty" correctly handles numeric values, putting zeros at the bottom.
3. [ ] **Integrity**: Ensure unit prices are formatted with the `$` prefix (e.g., $29.99).
