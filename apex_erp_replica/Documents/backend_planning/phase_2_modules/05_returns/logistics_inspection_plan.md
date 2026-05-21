# Non-Blind Implementation Plan: Returns Logistics & Inspection

## 1. UI Infrastructure Analysis
*Reference File: `Pages/logistics_inspection.html`*

The Returns Inspection view is a tactical warehouse tool. The following HTML structures must be targeted:

### 1.1. Inspection Queue (Left Column)
- **Container**: `.queue-card` (Line 154).
- **Target Items**: `.queue-item` list (Line 157).
    - Status Indicator: (Line 160). (e.g., "PENDING", "COMPLETE").
    - Logic: Selecting an item updates the assessment panel (Right Column).

### 1.2. Assessment Panel (Right Column)
- **Item Header**: `.card-header` (Line 167).
- **Condition Grading**: `.condition-btn` group (Lines 173-175).
    - Logic: Click toggles `.selected` class. Maps to `condition_code` in API.
- **Verification Checklist**: `input[type="checkbox"]` group (Lines 180-187).
- **Final Disposition**: `select` (Line 192). (Options: Return to Stock, Salvage, RTV).

### 1.3. Workflow Controls
- **Action Buttons**: `.card-footer` (Lines 200-205).
    - Save Draft.
    - Complete & Confirm: Triggers `PATCH /api/v1/returns/{id}/inspect`.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/logistics_inspection_spec.md`*

| Spec Key | API JSON Path | Functional UI Mapping |
| :--- | :--- | :--- |
| `expected_qty` | `items[].expected_qty` | Info Label in Queue (Line 159) |
| `condition_code` | `line_results[].condition`| Condition Button Selection State |
| `disposition` | `line_results[].disposition`| Disposition Dropdown Value |
| `checks` | `line_results[].checks` | Checklist Boolean States |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Warehouse Verification Engine
1. `GET /api/v1/returns/{id}/inspect`:
    - Fetch items for the return and their required checklist schemas.
2. `PATCH /api/v1/returns/{id}/inspect`:
    - **Grading Update**: Update condition and disposition in `log_return_items`.
    - **Status Promotion**: If all items are inspected, set `log_returns.status` to `inspected`.
    - **Inventory Sync**: If disposition is 'Restock', create a pending inventory receipt.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/logistics_inspection.js`*

1. **Selection Manager**:
```javascript
function selectItem(lineId) {
    document.querySelectorAll('.queue-item').forEach(i => i.classList.remove('active'));
    // Update active class...
    // Populate Right Column with data for lineId...
}
```
2. **Grade Toggle**:
```javascript
document.querySelectorAll('.condition-btn').forEach(btn => {
    btn.onclick = () => {
        // Toggle selected class and update internal state...
    };
});
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/logistics_inspection.html`. Confirm the "Active" queue item (Line 157) has the blue border styling.
2. [ ] **Precision**: Verify that the disposition dropdown (Line 192) includes "Return to Stock" as the default selected option.
3. [ ] **Integrity**: Ensure "Complete & Confirm" (Line 203) performs a PATCH request and redirects to the parent return details page.
