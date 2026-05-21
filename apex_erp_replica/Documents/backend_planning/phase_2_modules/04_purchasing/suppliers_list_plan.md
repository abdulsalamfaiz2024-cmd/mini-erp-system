# Non-Blind Implementation Plan: Suppliers List

## 1. UI Infrastructure Analysis
*Reference File: `Pages/suppliers_list.html`*

The Suppliers List is the master directory for vendors. The following HTML structures must be targeted:

### 1.1. Directory Controls
- **Global Search**: `.search-bar input` (Line 189).
- **Payment Terms Filter**: `select` (Line 193).
- **Status Filter**: `select` (Line 201). (Populated with Active/Inactive).

### 1.2. Directory Table
- **Table Body**: `.data-table tbody` (Line 222).
- **Row Columns**:
    - `Checkbox`: Col 1.
    - `Supplier Name`: Col 2 (accent blue, clickable). Targets `supplier_details.html?id=[val]`.
    - `Contact Person`: Col 3.
    - `Phone`: Col 4.
    - `Email`: Col 5.
    - `Payment Terms`: Col 6.
    - `Actions`: Col 7 (3-dots placeholder).

### 1.3. Navigation Logic
- **Pagination**: `.pagination` (Line 278).
- **Counter**: `span` at Line 279. (e.g., "Showing 1-5 of 100").

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/suppliers_list_spec.md`*

| Spec Key | API JSON Path | Functional UI Mapping |
| :--- | :--- | :--- |
| `suppliers[]` | `suppliers` | Rows inside `.data-table tbody` |
| `supplier_id` | `suppliers[].supplier_id` | Attached to Name link: `?id={val}` |
| `payment_terms` | `suppliers[].payment_terms`| Col 6 text |
| `total_count` | `root.total_count` | Pagination summary label |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Supplier Directory Service
1. `GET /api/purchasing/suppliers`:
    - `SELECT * FROM mst_suppliers`.
    - Apply complex filtering:
        - `WHERE name ILIKE %q% OR contact ILIKE %q%`
        - `AND status = :status`
        - `AND payment_terms = :terms`
    - Apply pagination: `LIMIT :limit OFFSET (:page - 1) * :limit`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/suppliers_list.js`*

1. **Mass Selection Logic**:
```javascript
headerCheckbox.onclick = () => {
    document.querySelectorAll('tbody input[type="checkbox"]').forEach(c => c.checked = headerCheckbox.checked);
};
```
2. **Dynamic Redirection**: Ensures the click handler on Col 2 uses the `supplier_id` from the data object.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/suppliers_list.html`. Confirm that clicking the "Supplier Name" triggers a redirect to `supplier_details.html`.
2. [ ] **Precision**: Verify that the "Showing X-Y of Z" label correctly updates after a search operation.
3. [ ] **Integrity**: Ensure the "Status" filter correctly toggle between Active and Inactive (Line 202).
