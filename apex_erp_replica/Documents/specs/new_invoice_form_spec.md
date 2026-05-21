# Page Specification: New Invoice Form

## 1. Overview
The New Invoice form allows users to generate professional invoices. It supports manual entry or linking to existing Sales Orders for automatic data population.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint / Source | Method |
| :--- | :--- | :--- | :--- |
| **Customer Dropdown** | `customer_id` | `GET /api/v1/master/customers` | `GET` |
| **Invoice Number** | `invoice_id` | `GET /api/v1/invoices/next-id` | `GET` |
| **Invoice Date** | `invoice_date` | Date Picker (Default Today) | N/A |
| **Due Date** | `due_date` | Date Picker | N/A |
| **Link to SO Toggle** | `link_to_so` (Boolean) | N/A | N/A |
| **SO Selection** | `sales_order_id` | `GET /api/v1/sales/orders` | `GET` |
| **Line Item - Item** | `items[].product_id`| `GET /api/v1/master/products` | `GET` |
| **Line Item - Desc** | `items[].description`| User Input | N/A |
| **Line Item - Qty** | `items[].qty` | User Input (Default 1) | N/A |
| **Line Item - Price** | `items[].unit_price` | User Input / Master Price | N/A |
| **Line Item - Amount**| `items[].row_total` | Calculated (Qty * Price) | N/A |
| **Tax Detail** | `tax_amount` | Calculated (Subtotal * Tax Rate) | N/A |
| **Total Amount** | `total_amount` | Calculated (Subtotal + Tax) | N/A |
| **Action: Submit** | `(All form data)` | `POST /api/v1/invoices/submit` | `POST` |
| **Action: Save Draft**| `(All form data)` | `POST /api/v1/invoices/draft` | `POST` |

## 3. Data Structure (API Contracts)

### A. Submission Payload (`POST /api/v1/invoices/submit`)
```json
{
  "customer_id": "CUST-445",
  "invoice_id": "INV-2023-001",
  "invoice_date": "2023-10-26",
  "due_date": "2023-11-26",
  "linked_so_id": "SO-2023-122",
  "items": [
    {
      "product_id": "PRD-221",
      "description": "Premium Consultation",
      "qty": 1,
      "unit_price": 500.00,
      "row_total": 500.00
    }
  ],
  "tax_rate": 10.0,
  "tax_amount": 50.0,
  "total_amount": 550.0,
  "status": "Sent"
}
```

## 4. Key Logical Rules
1. **SO Linking Logic**: If "Link to Sales Order" is checked and an SO is selected, the form should ideally auto-populate the Customer and Line Items based on the SO details.
2. **Real-time Calculation**: Any change in Qty or Unit Price must instantly update the `row_total` and the overall `Tax Details`.
3. **Draft Mode**: "Save Draft" allows saving without full validation (e.g., missing items or dates).
4. **Validation**: "Send Invoice" requires a Customer, at least one Item, and a valid Due Date.

## 5. Integration Workflow
1. **Entry Point**: This page is accessed via the "Create New Invoice" action on the `invoice_details.html` page (or a global quick action).
2. **Post-Submission**: Redirect user to the populated `invoice_details.html?id=[new_id]` upon success.
