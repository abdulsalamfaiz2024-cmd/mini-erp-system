# Page Specification: Credit Processing

## 1. Overview
Credit Processing is the final stage of the returns workflow. It allows finance staff to calculate the exact refund or credit amount based on item value and restocking fees, and then execute the financial transaction.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Financial Summary** | `financials` | `GET /api/v1/returns/{id}/credit-calc` | `GET` |
| **Restocking Fee Select**| `restocking_fee_pct` | `GET /api/v1/returns/{id}/credit-calc` | `GET` |
| **Credit Method Toggle** | `credit_method` | Part of POST payload | N/A |
| **Refund Amount Input** | `final_refund_amt` | Part of POST payload | N/A |
| **Process Payment Btn** | Request Body | `POST /api/v1/returns/{id}/process-credit` | `POST` |

## 3. Data Structure (API Contracts)

### A. Credit Calculation View (`GET /api/v1/returns/RET-2024-001/credit-calc`)
**Response:**
```json
{
  "return_id": "RET-2024-001",
  "original_order_id": "SO-875",
  "financials": {
    "item_value_total": 89.99,
    "shipping_paid": 12.00,
    "suggested_restocking_fee_pct": 10,
    "net_refundable_max": 101.99
  },
  "payment_original": {
    "method": "Visa **** 4455",
    "gateway_transaction_id": "tx_998877"
  }
}
```

### B. Process Credit (`POST /api/v1/returns/RET-2024-001/process-credit`)
**Request:**
```json
{
  "resolution_type": "refund",
  "amount": 92.99,
  "method": "original_payment",
  "notify_customer": true,
  "notes": "Restocking fee applied due to open box."
}
```

## 4. Logical Actions
- **Apply Fee**: Selecting a restocking fee percentage updates the Net Refundable amount in real-time.
- **Method Switch**: Toggles between "Original Payment Method" and "Store Credit Wallet".
- **Safety Lock**: "Process Refund" button requires confirmation as it triggers a live gateway call.

## 5. Integration Notes
- Linked from Return Details after inspection is complete.
- Once processed, the return status moves to 'Closed' and the Financial Activity history is updated.
