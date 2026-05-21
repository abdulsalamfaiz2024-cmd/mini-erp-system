# Page Specification: Invoice Details

## 1. Overview
The Invoice Details page provides a comprehensive view of a specific invoice's status, associated customer info, financial breakdown, and payment history.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Header** | `invoice_id`, `status` | `GET /api/v1/invoices/{id}` | `GET` |
| **Invoice Info** | `date_issued`, `due_date`, `sales_order_ref`, `currency` | `GET /api/v1/invoices/{id}` | `GET` |
| **Customer Info** | `customer.name`, `customer.contact`, `customer.address`, `customer.email`, `customer.phone` | `GET /api/v1/invoices/{id}` | `GET` |
| **Line Items** | `items[]` (code, description, qty, unit_price, tax, total) | `GET /api/v1/invoices/{id}` | `GET` |
| **Financials** | `subtotal`, `tax_total`, `grand_total`, `amount_paid`, `balance_due` | `GET /api/v1/invoices/{id}` | `GET` |
| **Payment History**| `payments[]` (date, method, amount, ref) | `GET /api/v1/invoices/{id}/payments` | `GET` |
| **Action: Edit** | `invoice_id` | N/A (Client Route) | N/A |
| **Action: Pay** | `invoice_id`, `payment_data` | `POST /api/v1/payments/record` | `POST` |
| **Action: Reminder**| `invoice_id` | `POST /api/v1/invoices/{id}/remind` | `POST` |
| **Action: Print** | N/A | N/A (Window Print) | N/A |

## 3. Data Structure (API Contracts)

### A. Invoice Detail Response (`GET /api/v1/invoices/INV-2024-1098`)
```json
{
  "invoice_id": "INV-2024-1098",
  "status": "Overdue",
  "invoice_info": {
    "date_issued": "Oct 25, 2024",
    "due_date": "Nov 24, 2024",
    "sales_order_ref": "SO-2024-5501",
    "currency": "USD"
  },
  "customer": {
    "name": "Acme Corp.",
    "contact": "John Smith",
    "address": "123 Main St, Suite 400, Anytown, CA 90210",
    "email": "john.smith@acme.com",
    "phone": "(555) 123-4567"
  },
  "items": [
    {
      "code": "PROD-001",
      "description": "Premium Widget Pro License",
      "qty": 5,
      "unit_price": 199.00,
      "tax": 9.95,
      "total": 1044.75
    },
    {
      "code": "SERV-002",
      "description": "Implementation Services (Hours)",
      "qty": 10,
      "unit_price": 150.00,
      "tax": 0.00,
      "total": 1500.00
    },
    {
      "code": "SUPP-003",
      "description": "Annual Support Plan",
      "qty": 1,
      "unit_price": 500.00,
      "tax": 25.00,
      "total": 525.00
    }
  ],
  "financials": {
    "subtotal": 2995.00,
    "tax_total": 149.75,
    "grand_total": 3144.75,
    "amount_paid": 0.00,
    "balance_due": 3144.75
  },
  "payments": []
}
```

## 4. Logical Actions
- **Record Payment**: Triggers a modal to input payment amount and method. Updates `amount_paid` and `status` if fully paid.
- **Send Reminder**: Dispatches an email to the customer contact. Returns success/fail notification.
- **Print**: Standardized PDF generation or browser print view formatted for local printing.
- **Status Highlighting**: Status "Overdue" must be rendered in `var(--accent-red)`.

## 5. Integration Notes
- **Linked from Dashboard**: "Outstanding Payments" table links directly to this page.
- **Linked from Sales Order**: "Generate Invoice" action on Sales Order Details redirects to this page after creation.
