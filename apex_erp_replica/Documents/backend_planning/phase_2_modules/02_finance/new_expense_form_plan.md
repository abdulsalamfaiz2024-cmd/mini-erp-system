# Non-Blind Implementation Plan: New Expense Form

## 1. UI Infrastructure Analysis
*Reference File: `Pages/new_expense_form.html`*

The New Expense Form is a data-collection interface for employee spend. The following HTML structures must be targeted:

### 1.1. Core Metadata (Column 1)
- **Expense ID**: `input[type="text"]` (Line 142). (Disabled, fetched from server).
- **Date**: `input[type="date"]` (Line 146). (Required).
- **Description**: `input[type="text"]` (Line 151). (Required).
- **Category**: `select` (Line 156). (Required, fetched from server).
- **Amount**: `input[type="number"]` (Line 167). (Required, step="0.01").

### 1.2. Payment & Attachments (Column 2)
- **Payment Method**: `select` (Line 174).
- **Receipt Upload Zone**: `div` with dashed border (Lines 184-191). Targets `POST /api/v1/uploads`.
- **Notes**: `textarea` (Line 195).

### 1.3. Footer Actions
- **Submit Button**: `.btn.btn-green` (Line 210) with text "Submit Expense".
- **Save Draft**: `.btn.btn-blue` (Line 207) with text "Save Draft".
- **Cancel**: `.btn.btn-gray` (Line 204).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/new_expense_form_spec.md`*

| Spec Key | UI Selector | Event / Method |
| :--- | :--- | :--- |
| `date` | `input[type="date"]` | Value captured in JSON body. |
| `category_id` | `select` (Line 156) | Fetched from `GET /api/v1/expenses/categories`. |
| `receipt_url` | `Upload Zone` (Line 184) | Populated after `POST /api/v1/uploads` returns success. |
| `status` | `N/A` | Toggle: "Submit" -> `pending` | "Save Draft" -> `draft`. |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Master Data Endpoints
The form requires lookup data before it can be filled:
1. `GET /api/v1/expenses/categories`: Populate categories (`Office`, `Travel`, etc.).
2. `GET /api/v1/expenses/next-id`: Get the next `EXP-YYYY-XXX` string.

### 3.2. Controller Logic: `create_expense`
1. **Security**: Record the `submitted_by` user ID using the current JWT token.
2. **Persistence**:
    - If `status == 'pending'`, perform strict validation.
    - If `status == 'draft'`, allow partial save.
3. **Workflow**: 
    - If an expense exceeds a threshold (e.g., $1000), update flag to `requires_manager_approval`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/new_expense.js`*

1. **Upload Handler**:
```javascript
uploadZone.onclick = () => fileInput.click();
fileInput.onchange = async () => {
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    const response = await ApexAPI.uploadReceipt(formData);
    previewZone.innerHTML = `<img src="${response.file_url}" />`;
    formData.receipt_url = response.file_url; // Store for final submit
};
```
2. **Edit Mode (Non-Blind Logic)**:
If the URL contains `?id=EXP-XXX`, the script must call `GET /api/v1/expenses/{id}` and populate all form values (including the receipt preview).

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/new_expense_form.html`. Ensure the `*` indicators match the `required` attributes in JS.
2. [ ] **File Lifecycle**: Verify that the uploaded file URL is successfully passed into the final `POST /api/v1/expenses` payload.
3. [ ] **Draft Persistence**: Verify that after saving a draft, the user can re-open the form and all values (including the uploaded receipt) are restored.
4. [ ] **Permissions**: Verify that a non-admin user cannot edit an expense that has an "Approved" or "Paid" status.
