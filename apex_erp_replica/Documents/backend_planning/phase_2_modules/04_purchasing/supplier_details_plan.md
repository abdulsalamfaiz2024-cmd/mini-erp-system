# Non-Blind Implementation Plan: Supplier Details

## 1. UI Infrastructure Analysis
*Reference File: `Pages/supplier_details.html`*

The Supplier Detail view is a 360-degree vendor profile. The following HTML structures must be targeted:

### 1.1. Profile Header
- **Breadcrumbs**: `.breadcrumbs` (Line 187). (Final span: Line 192).
- **Supplier Name**: `.page-title` (Line 201).
- **Action Buttons**: (Lines 203-205).
    - View Related POs: (Redirects to PO list with filter).
    - Edit Supplier.

### 1.2. Info Panes (Left Column)
- **Summary**: `.info-card` at Line 215. Target `Supplier ID` and `Status` (badge).
- **Contact**: `.info-card` at Line 231. Target `Contact`, `Email`, `Phone`, `Address`.
- **Payment**: `.info-card` at Line 255. Target `Terms`, `Currency`, `Bank Account`.

### 1.3. Tabbed Content (Right Column)
- **Tab Header**: `.tabs-header` (Line 274). (Product Catalog vs PO History).
- **Table Ledger**: `.data-table tbody` (Line 292).
- **Row Columns (Catalog)**:
    - `Product SKU`: Col 1.
    - `Product Name`: Col 2.
    - `Category`: Col 3.
    - `Unit Price`: Col 4 (font-weight: 600).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/supplier_details_spec.md`*

| Spec Key | API JSON Path | Target UI Data Field |
| :--- | :--- | :--- |
| `supplier_name` | `root.supplier_name` | Page Title and Breadcrumb |
| `products[]` | `products` | Product Catalog Table rows |
| `po_history[]` | `po_history` | (Switchable view) |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Profile Aggregator
1. `GET /api/purchasing/suppliers/{id}`:
    - Primary fetch from `mst_suppliers`.
2. `GET /api/purchasing/suppliers/{id}/products`:
    - Join `inv_products` with `pur_supplier_products`.
3. `GET /api/purchasing/suppliers/{id}/po-history`:
    - Query `pur_purchase_orders` where `supplier_id = :id`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/supplier_details.js`*

1. **Tab Switcher Engine**:
```javascript
function switchTab(tabName) {
    document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
    // Update active class...
    // Fetch and render table content based on tabName...
}
```
2. **Search Filter**: Debounced search for the product catalog table.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/supplier_details.html`. Confirm the "View Related POs" button (Line 203) correctly appends the `supplier_id` to the destination URL.
2. [ ] **Precision**: Unit prices in the catalog table must be formatted with the `$` prefix.
3. [ ] **Audit**: Ensure the "Status" badge in the Summary card (Line 222) uses the `status-badge-sm` class as defined in CSS Line 50.
