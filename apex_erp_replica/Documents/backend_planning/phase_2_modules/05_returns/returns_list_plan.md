# Non-Blind Implementation Plan: Returns List

## 1. UI Infrastructure Analysis
*Reference File: `Pages/returns_list.html`*

The Returns Management list is the central repository for reverse logistics tracking. The following HTML structures must be targeted:

### 1.1. Control Ribbon
- **New Return Button**: `.btn.btn-blue` (Line 158).
- **Search Component**: `.search-bar input` (Line 149).
- **Filter Suite**: `.filter-section` (Line 162).
    - Status: `select` at Line 165. (Map to API `status` param).
    - Reason: `select` at Line 174. (Map to API `reason` param).
    - Date Range: `input[type="date"]` at Lines 183, 187.

### 1.2. Operations Table
- **Table Body**: `.data-table tbody` (Line 208).
- **Row Architecture**:
    - `Checkbox`: Col 1.
    - `Return ID`: Col 2 (accent blue). Targets `return_details.html?id=[val]`.
    - `Date`: Col 3.
    - `Customer`: Col 4.
    - `Items`: Col 5. (e.g., "3 Items").
    - `Reason`: Col 6.
    - `Status`: Col 7 (pill classes: `pending|authorized|inspected|rejected`).
    - `Resolution`: Col 8.
    - `Action`: Col 9 (View button).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/returns_list_spec.md`*

| Spec Key | API JSON Path | Functional UI Mapping |
| :--- | :--- | :--- |
| `returns_list[]` | `returns_list` | Rows inside `.data-table tbody` |
| `return_id` | `returns_list[].return_id` | Col 2 Text and Action ID |
| `items_count` | `returns_list[].items_count`| Col 5 formatted string |
| `status` | `returns_list[].status` | Map text to pill class (INSPECTED -> inspected) |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Filtered Return Retrieval
1. `GET /api/v1/returns`:
    - `SELECT * FROM log_returns`.
    - Join `mst_customers` and `pur_sales_orders`.
    - Apply complex logic:
        - `WHERE (return_id ILIKE %q% OR customer.name ILIKE %q%)`
        - `AND status = :status`
        - `AND created_at BETWEEN :start AND :end`
    - Apply pagination: `LIMIT 20 OFFSET 0`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/returns_list.js`*

1. **Status CSS Resolver**:
```javascript
const STATUS_MAP = {
    'pending': 'pending',
    'authorized': 'authorized',
    'inspected': 'inspected',
    'rejected': 'rejected'
};
// Use in render loop: `<span class="status-pill ${STATUS_MAP[ret.status]}">${ret.status}</span>`
```
2. **Filter Trigger**: "Apply Filters" button at Line 189 gathers form state and re-fetches API.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/returns_list.html`. Confirm the "View" button (Line 218) and Return ID (Line 211) both route to `return_details.html`.
2. [ ] **Integrity**: Ensure the date inputs (Line 183/187) are correctly captured for the API request.
3. [ ] **Precision**: Verify that "Items" (Col 5) correctly pluralizes based on `items_count` (e.g. "1 Item" vs "3 Items").
