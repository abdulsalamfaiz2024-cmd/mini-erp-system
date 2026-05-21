# Non-Blind Implementation Plan: Stock Adjustment

## 1. UI Infrastructure Analysis
*Reference File: `Pages/stock_adjustment.html`*

The Stock Adjustment Form is a correction utility for inventory reconciliation. The following HTML structures must be targeted:

### 1.1. Header Context
- **Adjustment ID**: `input[type="text"]` (Line 141). (Generated via `GET /api/v1/inventory/adjustments/next-id`).
- **Warehouse**: `select` (Line 150). (Populated from `GET /api/v1/warehouses`).
- **Reason**: `select` (Line 161).

### 1.2. Adjustment Table (Interactive Rows)
- **Table Body**: `.data-table tbody` (Line 198).
- **Interactive Fields**:
    - `Product Search`: `input` (Line 201). (Triggers autocomplete).
    - `Adjustment Input`: `input[type="number"]` (Line 206). (System calculates `New Qty` on `change`).
    - `New Qty Display`: `.data-table td:nth-child(5)`. (Line 208).
    - `Remove Item`: `&times;` cell. (Line 211).
- **Add Row**: `.btn.btn-blue` (Line 230).

### 1.3. Submission Footer
- **Submit**: `.btn.btn-green` (Line 245).
- **Cancel**: `.btn.btn-gray` (Line 239).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/stock_adjustment_spec.md`*

| Spec Key | API JSON Path | UI Event / Target |
| :--- | :--- | :--- |
| `line_items[]` | `line_items` | Rows inside `.data-table tbody` |
| `adjustment_qty` | `line_items[].adjustment_qty`| Value from Col 4 input |
| `new_qty` | `line_items[].new_qty` | Auto-calculated label in Col 5 |
| `reason` | `root.reason` | Value from Reason dropdown |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Inventory Correction Logic
1. `GET /api/v1/inventory/adjustments/next-id`: Generate unique reference.
2. `POST /api/v1/inventory/adjustments`:
    - **Atomic Transaction**:
        - Iterate through `line_items`.
        - Update `inv_products.stock_qty` (Current + Adjustment).
        - Insert record into `inv_stock_movements` with `type='ADJUST'`.
        - Log the adjustment header in `inv_adjustments`.
    - **Calculated Constraint**: Ensure `new_qty` cannot be negative if the product forbids negative stock.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/stock_adjustment.js`*

1. **Auto-Calc Engine**:
```javascript
function onQtyChange(input) {
    const row = input.closest('tr');
    const current = parseInt(row.querySelector('.current-qty').dataset.val);
    const adjustment = parseInt(input.value) || 0;
    const newQtyCell = row.querySelector('.new-qty');
    const newQty = current + adjustment;
    newQtyCell.textContent = newQty;
    if (newQty < 0) newQtyCell.classList.add('overdue');
}
```
2. **Add Row Utility**:
```javascript
function addLineItem() {
    const tbody = document.querySelector('.data-table tbody');
    const newRow = templateRow.cloneNode(true);
    tbody.appendChild(newRow);
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/stock_adjustment.html`. Ensure the `Adjustment ID` field is indeed `disabled`.
2. [ ] **Autocomplete**: Verify that selecting a product from the search input auto-populates the "SKU" and "Current Qty" cells in that row.
3. [ ] **Submission**: Ensure that "Damaged Goods" (Line 161) results in a negative `adjustment_qty` being sent to the server.
