# Non-Blind Implementation Plan: New Sales Order Form

## 1. UI Infrastructure Analysis
*Reference File: `Pages/new_sales_order_form.html`*

The New Sales Order Form is a data-entry interface with multiple reactive zones. The following HTML structures must be targeted:

### 1.1. Customer Information (Column 1)
- **Customer Select**: `.form-group select` (Line 145).
- **Billing Address**: `.form-group textarea` (Line 155).
- **Shipping Address**: `.form-group textarea` (Line 159).
- **Contact Details**: Inputs for name and email (Lines 166-170).

### 1.2. Order Details (Column 2)
- **Order Date**: `input[type="date"]` (Line 182).
- **Order #**: `input[type="text"]` (Line 186). (Disabled, fetched from server).
- **Salesperson**: `select` (Line 192).
- **Payment Terms**: `select` (Line 201).
- **Due Date**: `input[type="text"]` (Line 210). (Disabled, auto-calculated).

### 1.3. Line Items Table (Interactive)
- **Table Body**: `.data-table tbody` (Line 236).
- **Row Inputs**:
    - Product: `input[type="text"]` with type-ahead.
    - Qty: `input[type="number"]`.
    - Price: `input[type="text"]`.
    - Discount/Tax: `input[type="number"]`.
- **Add Item Button**: `.btn.btn-blue` (Line 263).
- **Remove Item**: `&times;` (Line 246).

### 1.4. Summary & Actions
- **Finance Labels**: `.summary-table` spans (Lines 266-277).
- **Submit Button**: `.btn.btn-green` (Line 315).
- **Save Draft**: `.btn.btn-blue` (transparent) (Line 312).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/new_sales_order_form_spec.md`*

| Spec Key | UI Selector | Event Trigger |
| :--- | :--- | :--- |
| `customer_id` | `select[name="customer"]` | `onchange` (Fetch address) |
| `items[]` | `.data-table tbody tr` | `oninput` (Recalculate total) |
| `due_date` | `input[name="due_date"]` | Derived from `Payment Term` + `Order Date` |
| `grand_total` | `.summary-row.total span` | Live calculation |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Master Data Endpoints
The form requires lookup data before it can be filled:
1. `GET /api/v1/master/customers`: Populate the customer dropdown.
2. `GET /api/v1/master/products`: Support the line item search.
3. `GET /api/v1/sales/orders/next-id`: Get the auto-incremented `SO-XXXX` string.

### 3.2. Order Submission Logic (`POST /api/v1/sales/orders/submit`)
1. **Validation**: 
    - Check if `customer_id` exists.
    - Verify every `product_id` in `items[]` is valid and has sufficient stock.
2. **Transaction**:
    - Insert into `sls_orders` (Header).
    - Loop and insert into `sls_order_items` (Lines).
    - Update `inv_products.stock_qty` (Commit inventory).
3. **Draft Mode**: If `is_draft` is true, bypass stock validation and mandatory field checks.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/new_sales_order.js`*

1. **Reactive Calculations**:
```javascript
function updateTotals() {
    let subtotal = 0;
    document.querySelectorAll('.line-item-row').forEach(row => {
        const qty = parseFloat(row.querySelector('.qty-input').value) || 0;
        const price = parseFloat(row.querySelector('.price-input').value) || 0;
        subtotal += qty * price;
    });
    // Update summary spans...
}
```
2. **Address Auto-Fill**:
```javascript
customerSelect.onchange = async () => {
    const data = await ApexAPI.getCustomer(this.value);
    billingTextArea.value = data.billing_address;
};
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/new_sales_order_form.html`. Ensure `handleFormSubmit` is attached to the green button.
2. [ ] **Stock Locking**: Backend must reject submission if any item quantity exceeds `inv_products.available_stock`.
3. [ ] **Redirect**: Successful POST must capture the returned `order_id` and redirect to `sales_order_details.html?id=[order_id]`.
