# Phase 2 Plan: Module Development (Models & Controllers)

## 1. Objective
Convert the 30 technical specifications into functional Database Models and Logic Controllers.

---

## 2. Implementation Sub-Phases

### Phase 2.1: Master Data Schema
- **Target**: Customers, Products, Suppliers.
- **Workflow**:
    1. Read `customer_profile_spec.md`, `product_details_spec.md`.
    2. Create Pydantic schemas in `Backend/schemas/`.
    3. Create SQLAlchemy models in `Backend/models/`.
    4. Implement basic CRUD controllers in `Backend/controllers/`.

### Phase 2.2: Sales & Purchasing Logic
- **Target**: Sales Orders, Invoices, Purchase Orders.
- **Complexity**: High (Requires multi-table transactions).
- **Workflow**:
    1. Implement "Submit Order" logic (POST).
    2. Implement "Stock Validation" (Check if items exist before selling).
    3. Auto-generate IDs (e.g., SO-2023-XXX).

### Phase 2.3: Inventory & Finance Operations
- **Target**: Stock Adjustments, Ledger, Expenses.
- **Workflow**:
    1. Implement logic for Stock +/- on Goods Receipt.
    2. Implement "Journal Entry" creation during Invoice payment.

---

## 3. Reference Mapping
Every step here MUST cross-reference the corresponding `_spec.md` in `/Documents/specs/`.
- If `new_invoice_form_spec.md` defines `grand_total`, the Pydantic schema **must** use `grand_total`.
