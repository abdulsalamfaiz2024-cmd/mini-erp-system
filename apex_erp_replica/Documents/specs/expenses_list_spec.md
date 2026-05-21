# Page Specification: Expenses List

## 1. Overview
The Expenses List page displays all recorded expenses with filtering, search, and pagination capabilities. Users can view, edit, or delete expenses from this page.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Search Input** | `q` (query string) | `GET /api/v1/expenses?q={query}` | `GET` |
| **Date Range Filter** | `start_date`, `end_date` | `GET /api/v1/expenses?start={date}&end={date}` | `GET` |
| **Category Filter** | `category` | `GET /api/v1/expenses?category={id}` | `GET` |
| **Status Filter** | `status` | `GET /api/v1/expenses?status={status}` | `GET` |
| **Expenses Table** | `expenses[]` | `GET /api/v1/expenses` | `GET` |
| **Add Expense Button** | N/A | Links to `new_expense_form.html` | N/A |
| **Edit Action** | `expense_id` | Links to `new_expense_form.html?id={id}` | N/A |
| **Delete Action** | `expense_id` | `DELETE /api/v1/expenses/{id}` | `DELETE` |
| **Pagination** | `page`, `per_page` | `GET /api/v1/expenses?page={n}` | `GET` |

## 3. Data Structure (API Contracts)

### A. Expenses List (`GET /api/v1/expenses`)
**Request Query Parameters:**
- `q` (optional): Search term
- `category` (optional): Category filter
- `status` (optional): Pending, Approved, Rejected
- `start_date`, `end_date` (optional): Date range
- `page`, `per_page` (optional): Pagination

**Response:**
```json
{
  "expenses": [
    {
      "expense_id": "EXP-2023-001",
      "date": "2023-10-29",
      "description": "Office Supplies",
      "category": "Office",
      "amount": 450.00,
      "submitted_by": "John Doe",
      "status": "Approved",
      "receipt_attached": true
    },
    {
      "expense_id": "EXP-2023-002",
      "date": "2023-10-28",
      "description": "Client Dinner",
      "category": "Entertainment",
      "amount": 285.50,
      "submitted_by": "Jane Smith",
      "status": "Pending",
      "receipt_attached": true
    },
    {
      "expense_id": "EXP-2023-003",
      "date": "2023-10-27",
      "description": "Travel - NYC Trip",
      "category": "Travel",
      "amount": 1250.00,
      "submitted_by": "John Doe",
      "status": "Approved",
      "receipt_attached": true
    }
  ],
  "summary": {
    "total_expenses": 45,
    "total_amount": 28500.00,
    "pending_count": 8,
    "approved_count": 35,
    "rejected_count": 2
  },
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 45
  }
}
```

### B. Expense Categories (`GET /api/v1/expenses/categories`)
```json
{
  "categories": [
    { "id": 1, "name": "Office" },
    { "id": 2, "name": "Travel" },
    { "id": 3, "name": "Entertainment" },
    { "id": 4, "name": "Utilities" },
    { "id": 5, "name": "Marketing" }
  ]
}
```

### C. Delete Expense (`DELETE /api/v1/expenses/{id}`)
**Response:**
```json
{
  "success": true,
  "message": "Expense deleted successfully"
}
```

## 4. Logical Actions
- **Search**: Debounced search (300ms) filters by description or ID.
- **Filter**: Category and status dropdowns filter the table.
- **Status Badges**:
  - `Approved`: Green badge
  - `Pending`: Yellow badge
  - `Rejected`: Red badge
- **Add Expense**: Navigates to `new_expense_form.html`.
- **Edit**: Navigates to `new_expense_form.html?id={expense_id}`.
- **Delete**: Confirmation modal, then DELETE API call.

## 5. Integration Notes
- Linked from Finance Dashboard as subpage.
- Uses standard table and pagination from `main.css`.
