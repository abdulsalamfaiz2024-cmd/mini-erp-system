# Page Specification: Customer Profile & List

## 1. Overview
The Customer Profile page serves as the central hub for managing client relationships. It features a comprehensive searchable list of all customers and a detailed "Quick View" profile panel that provides a 360-degree view of a customer's financial standing, order history, and contact details.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Customer Search** | `query` (string) | `GET /api/v1/customers?q={query}` | `GET` |
| **Customer List Table** | `customers[]` (id, name, contact, email, phone, address, total_orders, balance) | `GET /api/v1/customers` | `GET` |
| **Add New Customer** | `customer_data` (name, email, phone, address, etc.) | `POST /api/v1/customers` | `POST` |
| **Customer Profile Detail** | `id`, `name`, `lifetime_value`, `last_order_date`, `open_invoices`, `credit_limit` | `GET /api/v1/customers/{id}` | `GET` |
| **Recent Orders Tab** | `orders[]` (id, date, amount, status) | `GET /api/v1/customers/{id}/orders` | `GET` |
| **Invoices Tab** | `invoices[]` (id, date, amount, balance, status) | `GET /api/v1/customers/{id}/invoices` | `GET` |
| **Action: Edit Customer** | `customer_id` | `PATCH /api/v1/customers/{id}` | `PATCH` |
| **Action: View Detail** | `customer_id` | `N/A` (Triggers side panel/quick view) | `N/A` |

## 3. Data Structure (API Contracts)

### A. Customer List Response (`GET /api/v1/customers`)
```json
{
  "count": 145,
  "customers": [
    {
      "id": "CUST-1001",
      "name": "Acme Industries",
      "contact_person": "John Smith",
      "email": "john.s@acme.com",
      "phone": "(555) 123-4567",
      "address": "123 Main St, Anytown",
      "total_orders": 145,
      "outstanding_balance": 12500.00
    }
  ]
}
```

### B. Customer Profile Detail (`GET /api/v1/customers/CUST-1001`)
```json
{
  "id": "CUST-1001",
  "name": "Acme Industries",
  "overview": {
    "lifetime_value": 150000.00,
    "last_order_date": "2024-01-01",
    "open_invoices": 3,
    "credit_limit": 50000.00
  },
  "contact_details": {
    "email": "john.s@acme.com",
    "phone": "(555) 123-4567",
    "address": "123 Main St, Anytown",
    "billing_address": "456 Corp Plaza, Anytown",
    "shipping_address": "789 Factory Way, Anytown"
  }
}
```

## 4. Logical Actions
- **Search/Filter**: Updates the table content dynamically based on query string.
- **Toggle Quick View**: Clicking "View" on a table row or the row itself opens the detailed profile panel at the bottom or side.
- **Tab Switching**: Switching between "Overview", "Recent Orders", "Invoices", and "Contact Details" in the profile panel loads specific data subsets.
- **Add New Customer**: Opens a modal form to input new customer details.

## 5. Integration Notes
- **Linked from Header**: Global search should allow navigating directly to a customer profile.
- **Linked from Sales Order**: Clicking a customer name in a Sales Order should redirect to this profile page.
