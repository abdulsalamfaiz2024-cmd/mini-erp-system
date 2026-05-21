# Non-Blind Implementation Plan: Inventory Dashboard

## 1. UI Infrastructure Analysis
*Reference File: `Pages/inventory_dashboard.html`*

The Inventory Dashboard is the operational center for stock management. The following HTML structures must be targeted:

### 1.1. Summary Ribbons (3-Column Grid)
- **Target Value Labels**:
    - Stock Value: `.card:nth-child(1) .metric-value`. (Line 136).
    - Low Stock items: `.card:nth-child(2) .metric-value`. (Line 145).
    - Turnover: `.card:nth-child(3) .metric-value`. (Line 154).

### 1.2. Quick Action Router
- **Container**: `.quick-actions-grid` (Lines 167-180).
- **Buttons**:
    - Product List: First button (Line 168).
    - Stock Adjustment: Second button (Line 171).
    - Goods Receipt: Third button (Line 174).
    - Warehouse Locations: Fourth button (Line 177).

### 1.3. Stock Movement Log
- **Table Body**: `.data-table tbody` (Line 202).
- **Column Mapping**:
    - `PRODUCT NAME`: Col 1.
    - `SKU`: Col 2.
    - `TYPE`: Col 3 (Badge style per spec).
    - `QUANTITY`: Col 4 (Colored: Green for +, Red for -).
    - `DATE`: Col 5.
    - `WAREHOUSE`: Col 6.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/inventory_dashboard_spec.md`*

| Spec Key | API JSON Path | UI Target |
| :--- | :--- | :--- |
| `total_value` | `root.total_value` | Card 1 Metric Val |
| `movements[]` | `movements` | `.data-table tbody` |
| `type` | `movements[].type` | Badge class `in|out|adjust` |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Inventory Aggregation
1. `GET /api/v1/inventory/summary`:
    - Calculate value: `SUM(inv_products.stock_qty * inv_products.unit_cost)`.
    - Low stock check: `COUNT(*)` where `stock_qty <= reorder_point`.
2. `GET /api/v1/inventory/movements`:
    - Query `inv_stock_movements`.
    - Join `inv_products` and `mst_warehouses`.
    - Sort by `created_at DESC` Limit 10.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/inventory_dashboard.js`*

1. **Badge and Color Context**:
```javascript
function renderMovementRow(m) {
    const typeClass = m.type.toLowerCase(); // in, out, adjust
    const qtyColor = m.quantity > 0 ? '#166534' : '#991b1b';
    return `<tr>
        <td>${m.product_name}</td>
        <td>${m.sku}</td>
        <td><span class="type-badge ${typeClass}">${m.type}</span></td>
        <td style="color:${qtyColor}">${m.quantity > 0 ? '+' : ''}${m.quantity}</td>
        <td>${m.date}</td>
        <td>${m.warehouse}</td>
    </tr>`;
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/inventory_dashboard.html`. Confirm quick action buttons have correct `onclick` navigations.
2. [ ] **Precision**: Total Stock Value in the card must be formatted with commas for readability (e.g., $1,250,000).
3. [ ] **Threshold Action**: If `low_stock_count` > 0, the low stock metric card icon should remain Red (`red` class in Line 142).
