# Non-Blind Implementation Plan: Customer Profile & List

## 1. UI Infrastructure Analysis
*Reference File: `Pages/customers.html`*

The Customers page is a master-detail dashboard for CRM. The following HTML structures must be targeted:

### 1.1. Directory Controls
- **Global Search**: `.search-input-wrapper input` (Line 142).
- **Primary Actions**: (Lines 130, 148).
    - Edit Customer.
    - Add New Customer.

### 1.2. Client Registry Table
- **Table Body**: `.data-table tbody` (Line 166).
- **Row Columns**:
    - `Customer ID`: Col 1.
    - `Name`: Col 2 (font-weight: 600).
    - `Contact Person`: Col 3.
    - `Email`: Col 4.
    - `Phone`: Col 5.
    - `Address`: Col 6.
    - `Total Orders`: Col 7.
    - `Outstanding Balance`: Col 8.
    - `Actions`: Col 9 (Edit/View spans).
- **Selection Logic**: Clicking a row adds `.selected-row` class (Line 167) and updates the Quick View.

### 1.3. Quick View Panel (Contextual Detail)
- **Header**: `.quick-view-header h3` (Line 227). (Client Name).
- **Tabs**: `.tab-item` group (Lines 233-236). (Overview, Orders, Invoices, Contact).
- **Overview KPIs**: `.metric-grid` (Line 239).
    - Lifetime Value: (Line 242).
    - Last Order: (Line 246).
    - Open Invoices: (Line 250).
    - Credit Limit: (Line 254).

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/customer_profile_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `customers[]` | `customers` | Rows mapping for main directory |
| `lifetime_value`| `overview.lifetime_value` | KPI Box 1 in Quick View |
| `last_order_date`| `overview.last_order_date` | KPI Box 2 in Quick View |
| `outstanding_balance` | `customers[].outstanding_balance` | Col 8 in table |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Client Information Service
1. `GET /api/v1/customers`:
    - `SELECT * FROM mst_customers`.
    - Join `pur_sales_orders` to count total orders.
    - Fetch balance from Account Receivable ledger.
2. `GET /api/v1/customers/{id}`:
    - Detailed profile with historical aggregates (LTV, last order date).
3. `POST /api/v1/customers`:
    - Insert into `mst_customers`.
    - Initialize empty financial profile for the new client.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/customers.js`*

1. **Quick View Hydrator**:
```javascript
function showDetails(customerId) {
    // 1. Fetch /api/v1/customers/{id}
    // 2. Clear and rebuild .metric-grid
    // 3. Update header name and tab content...
}
```
2. **Row Interaction**:
```javascript
document.querySelectorAll('tbody tr').forEach(row => {
    row.onclick = () => {
        // Remove .selected-row from others, add to this.
        showDetails(row.dataset.id);
    };
});
```

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/customers.html`. Confirm that the "Quick View" panel (Line 225) is visible and contains the 4 metric cards as defined in Line 239.
2. [ ] **Precision**: Balance (Col 8) and Lifetime Value metric (Line 242) must be formatted as currency.
3. [ ] **Integrity**: Ensure "Last Order" (Line 246) correctly handles cases where a customer has no prior orders (e.g. "Never").
