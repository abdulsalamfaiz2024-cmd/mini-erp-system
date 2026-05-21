# Non-Blind Implementation Plan: Purchase Order Details

## 1. UI Infrastructure Analysis
*Reference File: `Pages/purchase_order_details.html`*

The Purchase Order Details page is the source of truth for high-value procurement. The following HTML structures must be targeted:

### 1.1. Status & Actions
- **Status Indicator**: `.status-badge-lg` (Line 200). (e.g., "Approved").
- **Receive Goods Button**: `.btn.btn-blue` (Line 210). (Targets `goods_receipt.html?po_id=[val]`).

### 1.2. Info Panes (Left Column)
- **Summary Grid**: `.summary-card-grid` (Line 221).
    - Labels: PO Number, Order Date, Supplier, Total Amount.
- **Line Item Ledger**: `.data-table tbody` (Line 248).
    - Mapping: Product ID, Description, Qty, Unit Price, Total.
- **Financial Tally**: Cells at Lines 285-296. (Subtotal, Tax, Total).

### 1.3. Sidebar Context (Right Column)
- **Supplier Contact**: `.info-block` (Line 310).
- **Shipping Destination**: `.info-block` (Line 318).
- **Payment Terms**: (Line 342).
- **Invoice Utility**: "Generate Invoice" button. (Line 351).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/purchase_order_details_spec.md`*

| Spec Key | API JSON Path | UI Target Block |
| :--- | :--- | :--- |
| `status` | `root.status` | Header Badge Text/Class |
| `line_items[]` | `line_items` | Rows in `.data-table tbody` |
| `shipping_address` | `root.shipping_address` | Info Text at Line 320 |
| `payment_terms` | `root.payment_terms` | Finance Details row |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Detailed PO Retrieval
1. `GET /api/purchasing/pos/{id}`:
    - Primary query from `pur_purchase_orders`.
    - Join `mst_suppliers` for contact info and name.
    - Join `pur_po_items` for the line items array.
    - Return a flat JSON composite structure per spec B.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/purchase_order_details.js`*

1. **Status Visibility Logic**:
```javascript
function updateUIBasedOnStatus(status) {
    const receiveBtn = document.querySelector('button[onclick*="goods_receipt"]');
    if (status === 'Received' || status === 'Cancelled') {
        receiveBtn.disabled = true;
        receiveBtn.style.opacity = '0.5';
    }
}
```
2. **Dynamic Breadcrumb**: Updates the final span (Line 188) with the actual `po_number` from API.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/purchase_order_details.html`. Confirm that "Product ID" uses the `PROD-###` format as seen in Line 260.
2. [ ] **Cross-Linking**: Verify that "Receive Goods" button correctly passes the `po_id` in the URL parameters.
3. [ ] **Precision**: Total amount in the Summary Grid (Line 237) should be formatted with large font size (20px) for emphasis.
