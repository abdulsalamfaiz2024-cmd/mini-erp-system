# Purchase Order Details Technical Specification

## A. UI-to-API Mapping Table

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| Status Badge | `status` | `/api/purchasing/pos/{id}` | GET |
| Order Summary | `po_number`, `order_date`, `supplier_name`, `total_amount` | `/api/purchasing/pos/{id}` | GET |
| Line Items Table | `line_items` | `/api/purchasing/pos/{id}` | GET |
| Supplier & Shipping | `contact_name`, `contact_email`, `contact_phone`, `shipping_address`, `delivery_instructions` | `/api/purchasing/pos/{id}` | GET |
| Financial Details | `payment_terms`, `currency` | `/api/purchasing/pos/{id}` | GET |

## B. API Data Contract

### GET `/api/purchasing/pos/{id}`
**Response:**
```json
{
  "po_number": "PO-12345",
  "status": "Approved",
  "order_date": "2023-10-26",
  "supplier_name": "Global Tech Supplies Inc.",
  "total_amount": 1575.00,
  "line_items": [
    {
      "product_id": "PROD-001",
      "description": "27\" 4K UHD Monitor",
      "quantity": 2,
      "unit_price": 450.00,
      "total": 900.00
    }
  ],
  "contact_name": "Jane Doe",
  "contact_email": "jane.doe@globaltech.com",
  "contact_phone": "(555) 123-4567",
  "shipping_address": "A.P. Inc. Warehouse, 123 Innovation Drive, Tech Park, TX 75001, United States",
  "delivery_instructions": "Deliver to loading dock B between 9 AM and 4 PM.",
  "payment_terms": "Net 30",
  "currency": "USD"
}
```

## C. Logic & Actions
- **Edit Button**: Navigates to `/Pages/new_purchase_order_form.html?id={id}&edit=true`.
- **Change Status Button**: Opens a dropdown/modal to change PO status (e.g., Receive, Cancel).
- **Receive Goods Button**: Navigates to `/Pages/goods_receipt.html?po_id={id}`.
- **Generate Invoice Button**: Triggers a process to create a draft invoice from the PO.
- **Breadcrumbs**: Navigate back to Purchasing Dashboard or PO List.
