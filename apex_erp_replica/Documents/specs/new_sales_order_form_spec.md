# Page Specification: New Sales Order Form (Refined)

## 1. Overview
The entry form for creating a new Sales Order. This interactive page is organized into logical sections: Customer Information, Order Details, Line Items, and Shipping Information. It features automated calculations for totals and due dates.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint / Source | Method |
| :--- | :--- | :--- | :--- |
| **Breadcrumbs** | `Home > Sales > New Order` | N/A (Static/Nav) | N/A |
| **Customer Name** | `customer_id` | `GET /api/v1/master/customers` | `GET` |
| **Billing Address**| `billing_address` | User Input / Auto-fill from Customer | N/A |
| **Shipping Address**| `shipping_address` | User Input / Auto-fill from Customer | N/A |
| **Contact Person** | `contact_person` | User Input | N/A |
| **Email Address** | `email` | User Input | N/A |
| **Order Date** | `order_date` | Local Date Pick (Default: Today) | N/A |
| **Order #** | `order_id` | `GET /api/v1/sales/orders/next-id` | `GET` |
| **Salesperson** | `salesperson_id` | `GET /api/v1/master/salespeople` | `GET` |
| **Payment Terms** | `payment_term_id` | `GET /api/v1/master/payment-terms` | `GET` |
| **Due Date** | `due_date` | Auto-calculated (Order Date + Term) | N/A |
| **Line Items Row** | `items[]` (product, qty, price, discount, tax) | `GET /api/v1/master/products` | `GET` |
| **Summary Table** | `subtotal`, `total_tax`, `grand_total` | Calculated from `items[]` | N/A |
| **Shipping Method**| `shipping_method` | `GET /api/v1/master/shipping-methods` | `GET` |
| **Carrier** | `carrier` | User Input | N/A |
| **Est. Delivery** | `est_delivery_date` | Date Pick | N/A |
| **Action: Submit** | `(All form data)` | `POST /api/v1/sales/orders/submit` | `POST` |
| **Action: Save Draft**| `(All form data)` | `POST /api/v1/sales/orders/draft` | `POST` |
| **Action: Cancel** | N/A | N/A (History Back) | N/A |

## 3. Data Structure (API Contracts)

### A. Submission Payload (`POST /api/v1/sales/orders/submit`)
```json
{
  "order_metadata": {
    "order_id": "SO-20231027-001",
    "order_date": "2023-12-01",
    "salesperson_id": "SP-005",
    "status": "Submitted"
  },
  "customer_details": {
    "customer_id": "CUST-992",
    "billing_address": "123 Business Rd, Suite 100",
    "shipping_address": "456 Warehouse Blvd",
    "contact_person": "John Smith",
    "email": "j.smith@acme.com"
  },
  "payment_details": {
    "term_id": "NET30",
    "due_date": "2023-12-31"
  },
  "items": [
    {
      "product_id": "PROD-101",
      "qty": 5,
      "unit_price": 1200.00,
      "discount_percent": 0.0,
      "tax_percent": 10.0,
      "row_total": 6600.00
    }
  ],
  "totals": {
    "subtotal": 7122.50,
    "total_tax": 712.25,
    "grand_total": 7834.75
  },
  "shipping_details": {
    "method": "FedEx Ground",
    "carrier": "FedEx",
    "est_delivery": "2023-12-05"
  }
}
```

## 4. Key Logical Rules
1. **Financial Integrity**: Grand Total must be re-calculated on every change to Qty, Price, Discount, or Tax fields.
2. **Term-Based Dates**: If `Payment Terms` changes, `Due Date` must instantly update (e.g., Net 30 = Order Date + 30 days).
3. **Drafting Policy**: `Save Draft` sends the same object as `Submit` but with `status: "Draft"`, allowing for incomplete data.
4. **Validation**: `Submit` requires `customer_id`, `items[]` (at least one), and `order_date` to be valid.
5. **Navigation**: On successful Submit, route to `/Pages/sales_order_details.html?id=[order_id]`.
