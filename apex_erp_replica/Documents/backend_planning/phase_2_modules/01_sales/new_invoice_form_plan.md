# Non-Blind Implementation Plan: New Invoice Form

## 1. UI Infrastructure Analysis
*Reference File: `Pages/new_invoice_form.html`*

The New Invoice Form is a dual-entry system (Manual vs. SO-Linked). The following HTML structures must be targeted:

### 1.1. Core Metadata (Left Column)
- **Customer Select**: `.form-group select` (Line 180).
- **Invoice Date**: `input[type="text"]` (Line 190). *Note: Needs flatpickr or similar since it's type="text".*
- **Due Date**: `input[type="text"]` (Line 194).
- **SO Toggle Section**: 
    - Checkbox: `.checkbox-group input` (Line 200).
    - SO Select: `select` (Line 202).

### 1.2. Automated Fields (Right Column)
- **Invoice Number**: `input[type="text"]` (Line 213). (Disabled).

### 1.3. Line Items Table (Reactive)
- **Table Body**: `.data-table tbody` (Line 237).
- **Row Selectors**:
    - Item Select: `select` within `td` (Line 240).
    - Desc Input: `input` (Line 246).
    - Qty Input: `input[type="number"]` (Line 250).
    - Price Container: `div` with `input[type="text"]` (Lines 254-257).
- **Add Row Button**: `.btn.btn-blue` (Line 264) with text "Add Line Item".

### 1.4. Summary & Footer Actions
- **Tax/Total Labels**: `.summary-table` spans (Lines 269-279).
- **Submit Button**: `.btn.btn-blue` (Line 291) with text "Send Invoice". Special styling: `background-color: #2d3748`.
- **Save Draft**: `.btn.btn-blue` (Line 290) with text "Save Draft".

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/new_invoice_form_spec.md`*

| Spec Key | UI Selector | Behavioral Logic |
| :--- | :--- | :--- |
| `customer_id` | `select` (Line 180) | Fetch from `GET /api/v1/master/customers`. |
| `linked_so_id` | `select` (Line 202) | Triggered when checkbox (Line 200) is checked. |
| `items[]` | `.line-item-row` | If `linked_so_id` is selected, fetch SO lines and populate rows. |
| `tax_amount` | `.summary-row span` | Fixed 10% calculation applied to Subtotal. |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Conversion Logic
The most critical part of this module is the **Sales Order to Invoice** transformation.
1. `GET /api/v1/sales/orders/{id}/to-invoice`:
    - Fetch the SO.
    - Map `sls_order_items` -> `fin_invoice_items`.
    - Return a pre-filled JSON to the frontend.

### 3.2. Controller Logic: `submit_invoice`
1. **Financial Lock**: If linked to an SO, verify the SO is not already fully invoiced to prevent double-billing.
2. **Persistence**:
    - Create `fin_invoices` (Header).
    - Create `fin_invoice_items` (Lines).
    - **Ledger Integration**: Create a Journal Entry (Debit: Accounts Receivable, Credit: Sales Revenue, Credit: Tax Liability).

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/new_invoice.js`*

1. **SO Link Handler**:
```javascript
soToggle.onchange = (e) => {
    soSelect.disabled = !e.target.checked;
};

soSelect.onchange = async () => {
    const prefilledData = await ApexAPI.getSOForInvoice(this.value);
    populateForm(prefilledData); // Sets customer and lines
};
```
2. **Input Normalization**:
Since "Unit Price" has a preceding `$` span, the scraper must only target the `input` value and treat it as a float.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/new_invoice_form.html`. Ensure the footer is sticky as per style (Line 286).
2. [ ] **Validation**: "Send Invoice" must fail if any row has `0.00` price unless authorized.
3. [ ] **SO State**: Verify that after successful submission, the linked SO's status in the database is updated to `INVOICED`.
