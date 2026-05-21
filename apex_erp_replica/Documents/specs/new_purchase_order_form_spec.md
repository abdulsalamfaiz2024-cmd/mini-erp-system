# New Purchase Order Form Technical Specification

## A. UI-to-API Mapping Table

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| Supplier (Search) | `supplier_id` | `/api/purchasing/suppliers/search` | GET |
| PO Number (Read-only) | `po_number` | - | - |
| Order Date | `order_date` | - | - |
| Payment Terms | `payment_terms` | - | - |
| Expected Delivery Date | `delivery_date` | - | - |
| Shipping Address | `shipping_address` | - | - |
| Line Items | `line_items` (Array of objects) | - | - |
| Subtotal | `subtotal` | - | - |
| Tax | `tax` | - | - |
| Shipping | `shipping_cost` | - | - |
| Grand Total | `grand_total` | - | - |
| Notes | `notes` | - | - |
| Submit Button | All above fields | `/api/purchasing/pos/create` | POST |
| Save Draft Button | All above fields | `/api/purchasing/pos/save-draft` | POST |

## B. API Data Contract

### POST `/api/purchasing/pos/create`
**Request Body:**
```json
{
  "supplier_id": "SUP-12345",
  "order_date": "2023-10-27",
  "payment_terms": "Net 30",
  "delivery_date": "2023-11-15",
  "shipping_address": "123 Innovation Drive, Tech Park, Silicon Valley, CA 94043, USA",
  "line_items": [
    {
      "product_id": "PROD-101",
      "product_name": "Pro Wireless Mouse X1",
      "quantity": 10,
      "unit_price": 49.99
    }
  ],
  "subtotal": 1147.40,
  "tax": 91.79,
  "shipping_cost": 50.00,
  "grand_total": 1289.19,
  "notes": "Add any internal notes..."
}
```

## C. Logic & Actions
- **Add Item Button**: Appends a new blank row to the line items table.
- **Remove Item (Icon)**: Removes the corresponding row from the line items table.
- **Line Item Calculation**: Automatically updates Subtotal, Tax, and Grand Total whenever quantity or unit price changes.
- **Submit for Approval**: Sends POST request and navigates to `/Pages/purchase_order_list.html` upon success.
- **Save Draft**: Sends POST request and displays success notification.
- **Cancel**: Navigates back to `/Pages/purchase_order_list.html`.
