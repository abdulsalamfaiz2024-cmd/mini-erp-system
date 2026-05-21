# Suppliers List Technical Specification

## A. UI-to-API Mapping Table

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| Search Bar | `query` | `/api/purchasing/suppliers` | GET |
| Payment Terms Filter| `payment_terms` | `/api/purchasing/suppliers` | GET |
| Status Filter | `status` | `/api/purchasing/suppliers` | GET |
| Suppliers Table | `suppliers`, `total_count` | `/api/purchasing/suppliers` | GET |

## B. API Data Contract

### GET `/api/purchasing/suppliers`
**Query Parameters:** `query`, `payment_terms`, `status`, `page`, `limit`
**Response:**
```json
{
  "suppliers": [
    {
      "supplier_id": "SUP-001",
      "supplier_name": "Global Tech Supplies",
      "contact_person": "Sarah Johnson",
      "phone": "(555) 123-4567",
      "email": "sarah.j@globaltech.com",
      "payment_terms": "Net 30",
      "status": "Active"
    }
  ],
  "total_count": 100
}
```

## C. Logic & Actions
- **New Supplier Button**: Opens a modal or navigates to a new supplier form (not specified in current scope).
- **Search/Filter**: Triggers a re-fetch of the suppliers list.
- **Supplier Name Link**: Navigates to `/Pages/supplier_details.html?id={supplier_id}`.
- **Row Action (...)**: Options for Edit, View History, Deactivate.
- **Pagination**: Navigate through pages.
