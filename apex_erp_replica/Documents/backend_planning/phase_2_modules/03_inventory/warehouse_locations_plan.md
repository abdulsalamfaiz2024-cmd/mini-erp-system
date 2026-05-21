# Non-Blind Implementation Plan: Warehouse Locations

## 1. UI Infrastructure Analysis
*Reference File: `Pages/warehouse_locations.html`*

The Warehouse Locations page is a geospatial management view. The following HTML structures must be targeted:

### 1.1. Action Bar
- **Add Warehouse Button**: `.btn.btn-blue` (Line 218).
- **Global Search**: `.search-input-wrapper input` (Line 226).

### 1.2. Warehouse Card Architecture
- **Container**: `.warehouse-grid` (Line 232).
- **Card Target Labels**:
    - Name & ID: `.warehouse-name` (Line 237) and `.warehouse-id` (Line 238).
    - Status: `.status-badge` (Line 240).
    - Address: (Line 243).
    - Utilization Label: `.warehouse-card span[style*="font-weight: 600"]` (Line 247).
    - Utilization Bar: `.utilization-fill` (Line 250). (Requires logic to set class `green|yellow|red`).
- **Stat Items**:
    - Zones: `.stat-item:nth-child(1) .stat-value`.
    - Bins: `.stat-item:nth-child(2) .stat-value`.
    - Stock Value: `.stat-item:nth-child(3) .stat-value`.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/warehouse_locations_spec.md`*

| Spec Key | API JSON Path | Functional UI Mapping |
| :--- | :--- | :--- |
| `utilization` | `warehouses[].utilization`| Set CSS width % and bar color class |
| `stock_value` | `warehouses[].stock_value`| Formatted string (e.g. $850k) |
| `total_zones` | `warehouses[].total_zones`| Col 1 in the card stat grid |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Warehouse Metrics Engine
1. `GET /api/v1/warehouses`:
    - `SELECT * FROM mst_warehouses`.
    - Subquery: `stock_value = SUM(qty * unit_cost)` from `inv_stock` join `inv_products`.
    - Subquery: `total_bins = COUNT(*)` from `mst_bins`.
    - Calculation: `utilization = (occupied_bins / total_bins) * 100`.
2. `POST /api/v1/warehouses`:
    - Standard CRUD operation on `mst_warehouses`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/warehouse_locations.js`*

1. **Utilization Color Resolver**:
```javascript
function getUtilizationClass(pct) {
    if (pct < 70) return 'green';
    if (pct < 85) return 'yellow';
    return 'red';
}
```
2. **Value Formatter**:
```javascript
function formatShortCurrency(val) {
    if (val >= 1000) return '$' + (val / 1000).toFixed(0) + 'k';
    return '$' + val;
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/warehouse_locations.html`. Confirm that utilization bars correctly use the `width` style based on API data.
2. [ ] **Precision**: Ensure the "Stock Value" in the card is formatted concisely (e.g., $850k instead of $850,000.00).
3. [ ] **Audit**: Verify that the "View Zones" button correctly passes the `warehouse_id` to the zones modal or subpage.
