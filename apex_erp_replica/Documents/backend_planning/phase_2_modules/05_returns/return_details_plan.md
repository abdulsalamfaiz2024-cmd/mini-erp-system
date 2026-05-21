# Non-Blind Implementation Plan: Return Details

## 1. UI Infrastructure Analysis
*Reference File: `Pages/return_details.html`*

The Return Detail view is the orchestration layer for reverse logistics. The following HTML structures must be targeted:

### 1.1. Status Context
- **Status Header**: `.status-header` (Line 160).
    - Status Text Target: `.status-header div:nth-child(2)` (Line 163). (e.g., "PENDING INSPECTION").
- **Primary Actions**: (Lines 166-168).
    - Print Label.
    - Inspect Items: (Redirects to `logistics_inspection.html`).

### 1.2. Main Ledger (Left Column)
- **Manifest Table**: `.data-table tbody` (Line 188).
    - Columns: SKU, Product, Qty, Condition (with styling).
- **Audit Timeline**: `.timeline` (Line 204).
    - Logic: Dynamically generate `.timeline-item` blocks for each entry in `activities[]`.

### 1.3. Decision Cards (Right Column)
- **Resolution Control**: `.action-card` at Line 221.
    - Target: Resolution Type text (Line 227).
    - Constraint Logic: Disable "Process Settlement" button (Line 229) if status != 'inspected'.
- **Customer Dossier**: `.action-card` at Line 234.
    - Target: Avatar, Name, and Company.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/return_details_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `status` | `root.status` | Header text and button availability |
| `items[]` | `items` | Manifest table rows |
| `activities[]` | `activities` | Timeline item generation |
| `customer` | `root.customer` | Sidebar Contact card |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Reverse Logistics Tracking
1. `GET /api/v1/returns/{id}`:
    - Primary fetch from `log_returns`.
    - Join `log_return_items` and `mst_customers`.
2. `PATCH /api/v1/returns/{id}/authorize`:
    - Update status to `authorized`.
    - Append to audit log.
3. `GET /api/v1/returns/{id}/history`:
    - Detailed query of `sys_audit_logs` filtered for target resource.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/return_details.js`*

1. **Timeline Generator**:
```javascript
function renderTimeline(activities) {
    const list = document.querySelector('.timeline');
    list.innerHTML = activities.map(a => `
        <div class="timeline-item">
            <div style="font-weight:600; font-size:13px;">${a.msg}</div>
            <div style="font-size:11px; color:var(--text-muted);">${a.date} • by ${a.user}</div>
        </div>
    `).join('');
}
```
2. **Button Guard**: Checks status on load and toggles the `disabled` attribute on the settlement button.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/return_details.html`. Confirm that "Condition" in the Items table (Line 185) defaults to "Uninspected" if no data is present.
2. [ ] **Context**: Verify the "Process Settlement" button (Line 229) is visually disabled in the HTML and requires status 'inspected' to unlock.
3. [ ] **Accuracy**: Ensure the "Inspect Items" button correctly passes the return ID in the URL.
