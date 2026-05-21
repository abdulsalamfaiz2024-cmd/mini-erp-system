# Page Specification: Sales Order Details

## 1. Overview
Detailed view for a specific Sales Order, displaying customer data, shipping info, line items, and financial totals.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Order Title** | `order_id` | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Status Badge** | `status` | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Customer Info Card** | `customer.name`, `customer.contact`, `customer.email`, `customer.phone`, `customer.billing_address`, `customer.shipping_address` | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Order Details Card** | `order_date`, `salesperson`, `payment_terms`, `shipping_method` | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Shipping Info Card** | `ship_date`, `tracking_number`, `est_delivery` | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Line Items Table** | `items[]` (`code`, `description`, `qty`, `unit_price`, `discount`, `total`) | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Financial Summary** | `subtotal`, `tax_percent`, `tax_amount`, `shipping_cost`, `total_amount` | `GET /api/v1/sales/orders/{id}` | `GET` |
| **Action: Edit** | `order_id` | `N/A` (Navigates to Edit Page) | `N/A` |
| **Action: Change Status**| `order_id`, `new_status` | `PUT /api/v1/sales/orders/{id}/status` | `PUT` |
| **Action: Gen Invoice** | `order_id` | `POST /api/v1/sales/orders/{id}/invoice` | `POST` |

## 3. Data Structure (API Contracts)

### A. Order Detail Response (`GET /api/v1/sales/orders/SO-10234`)
```json
{
  "order_id": "SO-10234",
  "status": "Processing",
  "customer": {
    "name": "Acme Corp.",
    "contact": "John Smith",
    "email": "john.smith@acme.com",
    "phone": "(555) 123-4567",
    "billing_address": "123 Main St, Suite 400, Anytown, USA",
    "shipping_address": "Same as Billing"
  },
  "order_details": {
    "order_date": "Oct 24, 2023",
    "salesperson": "Jane Doe",
    "payment_terms": "Net 30",
    "shipping_method": "FedEx Ground"
  },
  "shipping_info": {
    "ship_date": "Oct 26, 2023",
    "tracking_number": "1Z9999999999999999",
    "est_delivery": "Oct 30, 2023"
  },
  "items": [
    {
      "code": "A-1001",
      "description": "Laptop Pro X",
      "qty": 10,
      "unit_price": 1200.00,
      "discount": "5%",
      "total": 11400.00
    },
    {
      "code": "B-2002",
      "description": "Wireless Mouse",
      "qty": 20,
      "unit_price": 45.00,
      "discount": "0%",
      "total": 900.00
    },
    {
      "code": "C-3003",
      "description": "Keyboard, Mechanical",
      "qty": 15,
      "unit_price": 110.00,
      "discount": "0%",
      "total": 1650.00
    }
  ],
  "summary": {
    "subtotal": 13950.00,
    "tax_percent": 8,
    "tax_amount": 1116.00,
    "shipping_cost": 250.00,
    "total_amount": 15316.00
  }
}
```

## 4. Logical Actions
- **Edit Button**: Redirects to `/Pages/edit_sales_order.html?id=SO-10234`.
- **Change Status**: Opens a modal or dropdown to trigger status update API.
- **Generate Invoice**: Triggers creation of an invoice object in the backend and redirects to the new invoice.
- **Print**: Opens system print dialog for the current view.
