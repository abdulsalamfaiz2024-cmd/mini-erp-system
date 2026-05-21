# Non-Blind Implementation Plan: Purchase Order List

## 1. UI Infrastructure Analysis
*Reference File: `Pages/purchase_order_list.html`*

The Purchase Order List is the primary ledger for external procurement. The following HTML structures must be targeted:

### 1.1. List Controls
- **Global Search**: `.search-bar input` (Line 206).
- **Status Filter**: `select` (Line 210).
- **Date Filter**: `select` (Line 219).
- **Breadcrumb Navigation**: `.breadcrumbs` (Line 189).

### 1.2. Ledger Table
- **Table Body**: `.data-table tbody` (Line 240).
- **Row Columns**:
    - `PO #`: Col 1 (accent blue, clickable). Targets `purchase_order_details.html?id=[val]`.
    - `Date`: Col 2.
    - `Supplier`: Col 3.
    - `Total Amount`: Col 4 (font-weight: 500).
    - `Status`: Col 5 (pill classes: `approved|shipped|pending|received|cancelled`).
    - `Actions`: Col 6 (3-dots placeholder).

### 1.3. Navigation Logic
- **Pagination**: `.pagination` (Line 291).
- **Counter**: `span` at Line 292. (e.g., "Showing 1-5 of 150").

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/purchase_order_list_spec.md`*

| Spec Key | API JSON Path | UI Event / Target |
| :--- | :--- | :--- |
| `purchase_orders[]` | `purchase_orders` | Rows inside `.data-table tbody` |
| `po_id` | `purchase_orders[].po_id` | Col 1 Text and ID Param |
| `total_count` | `root.total_count` | Pagination summary label |
| `status` | `purchase_orders[].status` | Map text to pill class (e.g., CANCELLED -> cancelled) |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Procurement Query Engine
1. `GET /api/purchasing/pos`:
    - `SELECT * FROM pur_purchase_orders`.
    - Join `mst_suppliers`.
    - Apply complex filtering:
        - `WHERE supplier.name ILIKE %q% OR po_id ILIKE %q%`
        - `AND status = :status`
        - `AND created_at >= :start_date`
    - Apply pagination: `LIMIT :limit OFFSET (:page - 1) * :limit`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/purchase_order_list.js`*

1. **Status CSS Mapper**:
```javascript
const MAP = {
    'Approved': 'approved',
    'Shipped': 'shipped',
    'Pending': 'pending', 
    'Received': 'received',
    'Cancelled': 'cancelled'
};
// Use in render loop: `<span class="status-pill ${MAP[po.status]}">${po.status}</span>`
```
2. **Filter Sync**:
```javascript
function updateFilters() {
    const params = new URLSearchParams({
        query: searchInput.value,
        status: statusSelect.value,
        page: currentPage
    });
    fetchData('/api/purchasing/pos?' + params.toString());
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/purchase_order_list.html`. Ensure the "PO #" column is clickable and routes to `purchase_order_details.html`.
2. [ ] **Precision**: Total amount must be formatted as currency (e.g., $15,250.00).
3. [ ] **Integrity**: Verify that "Received" status uses the correct `status-pill received` class as defined in CSS Line 58.
