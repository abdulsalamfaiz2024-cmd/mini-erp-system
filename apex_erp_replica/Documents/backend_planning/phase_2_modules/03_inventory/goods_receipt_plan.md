# Non-Blind Implementation Plan: Goods Receipt

## 1. UI Infrastructure Analysis
*Reference File: `Pages/goods_receipt.html`*

The Goods Receipt Form is the entry point for vendor-supplied stock. The following HTML structures must be targeted:

### 1.1. Header Context
- **Receipt ID**: `input[type="text"]` (Line 141). (Generated via `GET /api/v1/inventory/receipts/next-id`).
- **Supplier**: `select` (Line 150). (Populated from `GET /api/v1/suppliers`).
- **PO Link**: `select` (Line 161). (Populated based on Supplier selection).
- **Warehouse**: `select` (Line 169).

### 1.2. Receipt Table (Matched against PO)
- **Table Body**: `.data-table tbody` (Line 200).
- **Columns**:
    - `Product`: Col 1.
    - `SKU`: Col 2.
    - `Ordered Qty`: Col 3. (Read-only, from PO).
    - `Received Qty`: Col 4. (Input, Line 206).
    - `Unit Price`: Col 5.
    - `Line Total`: Col 6. (Calculated: `Received Qty * Unit Price`).
- **Summary**: Total Value display at Line 243.

### 1.3. Documentation
- **Notes**: `textarea` (Line 255). (Required if quantities differ).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/goods_receipt_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `po_id` | `root.po_id` | Selection triggers table population |
| `received_qty`| `line_items[].received_qty` | Value from Table Col 4 Input |
| `unit_price` | `line_items[].unit_price`| Multiplier for Line Total |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Inventory Arrival Logic
1. `GET /api/v1/purchase-orders?supplier={id}`:
    - Return open POs for the selected vendor to drive the form.
2. `POST /api/v1/inventory/receipts`:
    - **Update Product Inventory**: Increment `stock_qty` in `inv_products`.
    - **Mark PO Status**:
        - If all items received: `PO Status = Received`.
        - If partial: `PO Status = Partially Received`.
    - **Finance Link**: Create a draft `AP Invoice` (Accounts Payable) based on the received value.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/goods_receipt.js`*

1. **PO Data Injection**:
```javascript
supplierSelect.onchange = async () => {
    const pos = await ApexAPI.getSupplierPOs(this.value);
    poSelect.innerHTML = pos.map(p => `<option value="${p.id}">${p.label}</option>`);
};

poSelect.onchange = async () => {
    const poDetails = await ApexAPI.getPO(this.value);
    renderTable(poDetails.items);
};
```
2. **Highlight Discrepancies**:
```javascript
function checkQty(input) {
    const ordered = parseInt(input.closest('tr').dataset.ordered);
    const received = parseInt(input.value);
    if (received !== ordered) {
        input.style.borderColor = '#f59e0b'; // Amber warning
    } else {
        input.style.borderColor = '';
    }
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/goods_receipt.html`. Ensure the total value `$3,660.00` correctly updates when `Received Qty` changes.
2. [ ] **Lookup**: Verify that changing the supplier resets the PO selection and clears the table.
3. [ ] **Inventory Integrity**: Ensure that confirming the receipt increments stock only in the *selected* Warehouse (Line 169).
