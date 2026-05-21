# Plan 3.2: Dynamic UI Binding & State Management (Exhaustive Detail)

## 1. Scope & Objective
This document outlines the protocol for removing static "placeholder" values from the HTML files and replacing them with dynamic data fetched from the API Bridge.

---

## 2. Binding Protocol per Page Type

### 2.1. List Views (Tables)
- **Target**: `expenses_list.html`, `returns_list.html`, etc.
- **Workflow**:
    1. HTML includes a `<tbody>` with a unique ID (e.g., `id="expenseTableBody"`).
    2. JavaScript fetches the array of data.
    3. Iterate through array using `.map()` or `.forEach()`.
    4. Inject rows using Template Literals.
    5. Handle pagination (Update `Next` / `Prev` buttons based on `total_count`).

### 2.2. Detail Views (Forms/Cards)
- **Target**: `invoice_details.html`, `product_details.html`.
- **Workflow**:
    1. Identify all `<span>` or `<div>` elements with data placeholders.
    2. Assign unique IDs (e.g., `id="fieldInvoiceNumber"`).
    3. On `DOMContentLoaded`, fetch the object by ID (`?id=XXX`).
    4. Populate fields: `document.getElementById('fieldInvoiceNumber').innerText = data.invoice_number`.

---

## 3. Form Submission Logic
- **Standard**: Every form must have a `onsubmit="handleFormSubmit(event)"` handler.
- **Validation**: Perform client-side check (e.g., "Empty Amount") before calling `ApexAPI`.
- **Feedback**: Disable the "Submit" button to prevent double-clicks; show success toast on completion.

---

## 4. Navigation & State Persistence
- **Active State**: The sidebar highlight logic in `main.js` must be extended to ensure sub-menus stay open even if a page is deep-linked.
- **URL Parameters**: Use `URLSearchParams` to extract IDs from the browser bar and pass them to the API Bridge.

---

## 5. Verification Steps
1. [ ] **Cross-Browser Test**: Verify that table rendering works in Chrome, Firefox, and Safari.
2. [ ] **Empty State Test**: Verify that if the API returns 0 records, a "No data found" message is displayed instead of a blank table.
3. [ ] **Latency Test**: Verify that the UI remains responsive during large data fetches (e.g., Ledger loading 1000 rows).
