# Non-Blind Implementation Plan: Sales Order Details

## 1. UI Infrastructure Analysis
*Reference File: `Pages/sales_order_details.html`*

The Sales Order Details page is a read-heavy management view. The following HTML structures must be targeted for dynamic binding:

### 1.1. Header & Status
- **Order ID Display**: `.page-title` (Line 129). (Current: "Sales Order Details: SO-10234")
- **Status Badge**: `.status-badge` (Line 130). Must update class based on status (e.g., `processing`, `delivered`, `cancelled`).

### 1.2. Action Buttons
- **Generate Invoice**: `.btn.btn-purple` (Line 137). Needs `onclick` to trigger the backend conversion.
- **Change Status**: `.btn.btn-green` (Line 136). Needs logic to show status selection.

### 1.3. Information Cards
- **Customer Card**: `.card:nth-child(1) .info-list` (Lines 151-176).
    - `Customer`: `.info-row:nth-child(1) .info-value`
    - `Contact`: `.info-row:nth-child(2) .info-value`
    - `Email`: `.info-row:nth-child(3) .info-value`
    - `Phone`: `.info-row:nth-child(4) .info-value`
    - `Billing Address`: `.info-row:nth-child(5) .info-value`
    - `Shipping Address`: `.info-row:nth-child(6) .info-value`
- **Order Details Card**: `.card:nth-child(2) .info-list` (Lines 186-203).
    - `Order Date`: `.info-row:nth-child(1) .info-value`
    - `Salesperson`: `.info-row:nth-child(2) .info-value`
    - `Payment Terms`: `.info-row:nth-child(3) .info-value`
    - `Shipping Method`: `.info-row:nth-child(4) .info-value`
- **Shipping Info Card**: `.details-column:nth-child(2) .card:nth-child(1) .info-list` (Lines 216-229).

### 1.4. Line Items Table & Summary
- **Table Body**: `.data-table tbody` (Line 250). Requires dynamic row injection.
- **Summary Section**: `.summary-table` (Lines 278-295).
    - `Subtotal`: `.summary-row:nth-child(1) span:nth-child(2)`
    - `Tax`: `.summary-row:nth-child(2) span:nth-child(2)`
    - `Shipping`: `.summary-row:nth-child(3) span:nth-child(2)`
    - `Total`: `.summary-row.total span:nth-child(2)`

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/sales_order_details_spec.md`*

| Spec Key | API Object Path | Linked UI Element |
| :--- | :--- | :--- |
| `order_id` | `root.order_id` | `.page-title` (SO-XXXXX) |
| `status` | `root.status` | `.status-badge` text & class |
| `name` | `customer.name` | Customer Info > Customer Val |
| `items` | `items[]` | `.data-table tbody` Rows |
| `total_amount` | `summary.total_amount` | `.summary-row.total` Val |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Entity Relationship Query
The detail view requires a complex join or multiple queries:
1. `SELECT * FROM sls_orders WHERE id = :id`
2. `JOIN mst_customers ON sls_orders.customer_id = mst_customers.id`
3. `SELECT * FROM sls_order_items JOIN inv_products ON ... WHERE order_id = :id`

### 3.2. Controller Logic (`Backend/controllers/sales_controller.py`)
- `get_order_details(id)`: Aggregates the order, customer, items, and summary into a single JSON response exactly matching Section 3 of the Spec.
- `generate_invoice(order_id)`: 
    - Verify order exists and is not already invoiced.
    - Create `fin_invoices` record copying amounts.
    - Update `sls_orders.status = 'INVOICED'`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/sales_order_details.js`*

1. **URL ID Extraction**: 
```javascript
const urlParams = new URLSearchParams(window.location.search);
const orderId = urlParams.get('id') || 'SO-10234'; // Fallback for dev
```
2. **Dynamic UI Update**:
```javascript
function renderDetails(data) {
    document.querySelector('.page-title').innerText = `Sales Order Details: ${data.order_id}`;
    document.querySelector('.status-badge').innerText = `Status: ${data.status}`;
    document.querySelector('.status-badge').className = `status-badge ${data.status.toLowerCase()}`;
    // ... populate info rows ...
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/sales_order_details.html`. Ensure selectors target the correct `.info-value` spans.
2. [ ] **Status Mapping**: Backend must return status strings (e.g., "Processing") and frontend must map to CSS classes (e.g., `processing`).
3. [ ] **Invoice Action**: Verify that clicking "Generate Invoice" triggers the POST call and redirects on success.
