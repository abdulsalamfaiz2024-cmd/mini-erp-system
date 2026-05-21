# Non-Blind Implementation Plan: Returns Credit Processing

## 1. UI Infrastructure Analysis
*Reference File: `Pages/credit_processing.html`*

The Credit Processing UI is the financial finalization of a return. The following HTML structures must be targeted:

### 1.1. Financial Calculator (Left Column)
- **Calculation Ledger**: `.calc-card` (Line 19).
    - `Item Value`: `.calc-row:nth-child(1) span:nth-child(2)` (Line 164).
    - `Shipping`: `.calc-row:nth-child(2) span:nth-child(2)` (Line 165).
    - `Restocking Fee`: `.calc-row:nth-child(3) span:nth-child(2)` (Line 167). (Uses `accent-red`).
- **Grand Total**: `.calc-total span:nth-child(2)` (Line 168). (Uses `accent-blue`).
- **Fee Logic**: `select` (Line 173). (Options: 0%, 10%, 25%).

### 1.2. Settlement Controls (Left Column)
- **Settlement Notes**: `textarea` (Line 186).

### 1.3. Payout Terminal (Right Column)
- **Method Selector**: `.payment-method` group (Lines 197, 203).
    - Logic: Click toggles `.selected` class.
- **Communication Toggle**: `input[type="checkbox"]` (Line 211). (Notify customer).
- **Execution Engine**: `.btn.btn-blue` (Line 220). Triggers `POST /api/v1/returns/{id}/process-credit`.

---

## 2. Technical Specification Alignment
*Reference File: `Documents/specs/credit_processing_spec.md`*

| Spec Key | API JSON Path | Functional Context |
| :--- | :--- | :--- |
| `item_value_total` | `financials.item_value_total` | Calculation Row 1 |
| `net_refundable_max`| `financials.net_refundable_max` | Subtotal before fees |
| `resolution_type` | `root.resolution_type` | Derived from payment method selection |
| `final_refund_amt` | `root.amount` | Final value in `.calc-total` |

---

## 3. Backend Implementation Strategy (Python)

### 3.1. Financial Resolution Gateway
1. `GET /api/v1/returns/{id}/credit-calc`:
    - Fetch origin order price data and return item counts.
    - Resolve suggested fee based on inspection condition.
2. `POST /api/v1/returns/{id}/process-credit`:
    - **Transaction logic**: Trigger simulated Gateway refund (Line 215).
    - **Ledger post**: Create a Credit Memo record in Finance.
    - **Closing**: Set `log_returns.status = 'closed'`.

---

## 4. Intermediary Execution Logic (JavaScript)
*Target: `assets/js/credit_processing.js`*

1. **Reactive Totalizer**:
```javascript
function recalculateTotal() {
    const feePct = parseFloat(document.querySelector('select').value);
    const itemVal = state.itemValue;
    const shipping = state.shipping;
    const feeAmt = itemVal * (feePct / 100);
    const net = itemVal + shipping - feeAmt;
    // Update UI elements...
}
```
2. **Method Selector**: Standard class toggler on `.payment-method` clicks.

---

## 5. Verification instructions for Next Model
1. [ ] **UI Sync**: Inspect `Pages/credit_processing.html`. Confirm that "Visa ending in 4455" (Line 200) serves as a placeholder for dynamic transaction data.
2. [ ] **Integrity**: Ensure the restocking fee (Line 167) correctly displays as a negative value with red styling.
3. [ ] **Safety**: Confirm the "Confirm & Process Refund" button (Line 220) text explicitly matches the specification's intent for final settlement.
