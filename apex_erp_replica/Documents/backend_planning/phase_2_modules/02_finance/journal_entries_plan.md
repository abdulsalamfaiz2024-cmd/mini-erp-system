# Non-Blind Implementation Plan: Journal Entries

## 1. UI Infrastructure Analysis
*Reference File: `Pages/journal_entries.html`*

The Journal Entries page is the audit log of all financial movements. The following HTML structures must be targeted:

### 1.1. Performance Stats (3-Column Ribbon)
- **Container**: `.metrics-grid` (Lines 138-160).
- **Target Value Labels**:
    - Total Debits: `.card:nth-child(1) .metric-value`. (Line 142).
    - Total Credits: `.card:nth-child(2) .metric-value`. (Line 149).
    - Unposted Count: `.card:nth-child(3) .metric-value`. (Line 156).

### 1.2. Audit Table (Complex Rowspans)
- **Table Body**: `.data-table tbody` (Line 194).
- **Row Transformation Logic**:
    - A single `JournalEntry` from the API (Section 3A of spec) usually consists of 2+ table rows.
    - **Header Row**: 
        - Cols 1, 2, 3, 7, 8 use `rowspan="n"` where n = `entry.lines.length`.
        - Col 4, 5, 6 show the *first* line's data.
    - **Subsequent Rows**: Show remaining lines (Only Cols 4, 5, 6).
- **Status Badges**: `.status-badge` with class `approved` (for Posted) or `pending` (for Draft).

### 1.3. Global Footer (Balance Check)
- **Table Foot**: `tfoot` (Line 267).
- **Validation Label**: `.tfoot td:last-child` (Line 272). (Should toggle between "Balanced" and "Out of Balance").

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/journal_entries_spec.md`*

| Spec Key | API JSON Path | Linked UI Context |
| :--- | :--- | :--- |
| `total_debits` | `root.total_debits` | Metric 1 Ribbon |
| `lines` | `journals[].lines[]` | Multi-row table rendering |
| `status` | `journals[].status` | Col 7 Badge Style |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Journal Aggregation Logic
A journal entry is a logical group of `fin_ledger` records sharing the same `transaction_id` or `reference_id`.
1. `GET /api/v1/finance/ledger/journals`:
    - Query `fin_ledger` group by `reference_id`.
    - Use `ARRAY_AGG` or separate mapping logic to nest lines within the journal object.
2. `POST /api/v1/finance/ledger/journals/{id}/post`:
    - Transition state from `DRAFT` to `POSTED`.
    - **Immutability Rule**: Once posted, a journal entry cannot be deleted or modified; it must be reversed with a new entry.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/journal_entries.js`*

1. **Table Renderer (Non-Blind Logic)**:
```javascript
function renderJournal(entry) {
    const n = entry.lines.length;
    let html = `<tr>
        <td rowspan="${n}">${entry.date}</td>
        <td rowspan="${n}">${entry.ref_id}</td>
        <td rowspan="${n}">${entry.description}</td>
        <td>${entry.lines[0].account}</td>
        <td>${entry.lines[0].debit}</td>
        <td>${entry.lines[0].credit}</td>
        <td rowspan="${n}">${entry.status}</td>
        <td rowspan="${n}">⋮</td>
    </tr>`;
    for (let i = 1; i < n; i++) {
        html += `<tr>
            <td>${entry.lines[i].account}</td>
            <td>${entry.lines[i].debit}</td>
            <td>${entry.lines[i].credit}</td>
        </tr>`;
    }
    return html;
}
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/journal_entries.html`. Confirm `tfoot` totals match the sum of visible rows.
2. [ ] **Integrity**: Verify that for every entry, sum of line debits == sum of line credits.
3. [ ] **Filtering**: Ensure the month/year filter (Line 171) correctly triggers a new API request `?month=X&year=Y`.
