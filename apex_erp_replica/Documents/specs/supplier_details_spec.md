# Supplier Details Technical Specification

## A. UI-to-API Mapping Table

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| Header Info | `supplier_name` | `/api/purchasing/suppliers/{id}` | GET |
| Supplier Summary | `supplier_id`, `status` | `/api/purchasing/suppliers/{id}` | GET |
| Contact Information | `primary_contact`, `email`, `phone`, `address` | `/api/purchasing/suppliers/{id}` | GET |
| Payment & Terms | `payment_terms`, `default_currency`, `bank_account` | `/api/purchasing/suppliers/{id}` | GET |
| Product Catalog Tab | `products` | `/api/purchasing/suppliers/{id}/products` | GET |
| PO History Tab | `po_history` | `/api/purchasing/suppliers/{id}/po-history` | GET |

## B. API Data Contract

### GET `/api/purchasing/suppliers/{id}`
**Response:**
```json
{
  "supplier_name": "Global Tech Inc.",
  "supplier_id": "GT-84321",
  "status": "Active",
  "primary_contact": "Elena Rodriguez",
  "email": "elena.r@globaltech.com",
  "phone": "+1 (555) 123-4567",
  "address": "123 Innovation Drive, Tech Park, CA 94043",
  "payment_terms": "Net 30",
  "default_currency": "USD",
  "bank_account": "**** **** **** 1234"
}
```

## C. Logic & Actions
- **Edit Supplier Info Button**: Opens edit view/modal.
- **View Related POs Button**: Navigates to `/Pages/purchase_order_list.html?supplier_id={id}`.
- **Product Catalog Search**: Filters products within the supplier's catalog.
- **Tab Switching**: Switches between Product Catalog and Purchase Order History.
- **Pagination**: Paginate through products or history records.
