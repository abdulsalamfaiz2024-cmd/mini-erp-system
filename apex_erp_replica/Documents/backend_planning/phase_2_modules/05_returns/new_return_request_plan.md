# Non-Blind Implementation Plan: New Return Request

## 1. UI Infrastructure Analysis
*Reference File: `Pages/new_return_request.html`*

The New Return Request is a multi-step intake wizard. The following HTML structures must be targeted:

### 1.1. Step 1: Order Nexus
- **Order Lookup Input**: (Line 184).
- **Link Button**: `.btn.btn-blue` (Line 186). Triggers `GET /api/v1/orders/lookup/{id}`.
- **Auto-Fill Fields**: Customer Name (Line 189) and Order Date (Line 191).

### 1.2. Step 2: Product Selection
- **Table Body**: `.data-table tbody` (Line 210).
- **Reactive Row Logic**:
    - `Checkbox`: Col 1.
    - `Return Qty`: `input[type="number"]` (Line 215). (Must be validated against "Sold" count in Col 3).

### 1.3. Step 3: Categorization
- **Reason Selection**: `select` (Line 231).
- **Resolution Path**: `select` (Line 239).
- **Evidence Dropzone**: Dummy dropzone at Line 248. (Requires file upload event listener).

### 1.4. Return Summary (Sticky Column)
- **Container**: `.summary-card` (Line 257).
- **Dynamic Labels**:
    - Original Total: (Line 260).
    - Est. Credit Value: (Line 262). (Logic: `sum(return_qty * unit_price)` from Step 2).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/new_return_request_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `order_id` | `root.order_id` | Resolved from Link Order action |
| `items[]` | `items` | Array of `{sku, qty}` from checked rows in table |
| `reason` | `root.reason` | Value from Reason dropdown |
| `resolution` | `root.resolution` | Value from Resolution dropdown |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Reverse Logistics Intake
1. `GET /api/v1/orders/lookup/{id}`:
    - Search `pur_sales_orders` for the ID.
    - Join `pur_sales_order_items` and `mst_customers`.
2. `POST /api/v1/returns`:
    - Insert into `log_returns` with `status='pending'`.
    - Insert line items into `log_return_items`.
    - Log an audit trail entry for the originating sales order.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/new_return_request.js`*

1. **Credit Calculator**:
```javascript
function updateCredit() {
    let total = 0;
    document.querySelectorAll('tbody tr').forEach(row => {
        if (row.querySelector('input[type="checkbox"]').checked) {
            const qty = parseInt(row.querySelector('input[type="number"]').value);
            const price = parseFloat(row.dataset.price); // Store price in data attrib
            total += qty * price;
        }
    });
    document.querySelector('.summary-value[style*="accent-blue"]').textContent = '$' + total.toFixed(2);
}
```
2. **Order Linker**: Executes on button click (Line 186), updates Step 1 inputs and populates Step 2 table.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/new_return_request.html`. Confirm that Step 2 table (Line 201) correctly shows "Sold" vs "Return" columns.
2. [ ] **Validation**: Ensure "Return" quantity cannot exceed "Sold" quantity for any item.
3. [ ] **Navigation**: Confirm that "Submit Request" (Line 266) correctly signals a transition to the details page.
