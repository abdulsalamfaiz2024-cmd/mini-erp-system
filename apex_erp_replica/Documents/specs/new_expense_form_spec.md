# Page Specification: New Expense Form

## 1. Overview
The New Expense Form allows users to submit new expense claims or edit existing ones. It includes fields for expense details, receipt upload, and approval workflow.

## 2. UI Components & Data Mapping

| UI Component | Data Keys (JSON) | API Endpoint | Method |
| :--- | :--- | :--- | :--- |
| **Expense ID** | `expense_id` | Auto-generated | N/A |
| **Expense Date** | `date` | Form field | N/A |
| **Description** | `description` | Form field | N/A |
| **Category Dropdown** | `category_id` | `GET /api/v1/expenses/categories` | `GET` |
| **Amount** | `amount` | Form field | N/A |
| **Payment Method** | `payment_method` | Form field | N/A |
| **Receipt Upload** | `receipt_file` | `POST /api/v1/uploads` | `POST` |
| **Notes** | `notes` | Form field | N/A |
| **Submit Button** | Request body | `POST /api/v1/expenses` | `POST` |
| **Save Draft Button** | Request body | `POST /api/v1/expenses` (status: draft) | `POST` |

## 3. Data Structure (API Contracts)

### A. Create Expense (`POST /api/v1/expenses`)
**Request:**
```json
{
  "date": "2023-10-29",
  "description": "Client Lunch Meeting",
  "category_id": 3,
  "amount": 125.50,
  "payment_method": "Corporate Card",
  "receipt_url": "/uploads/receipts/receipt_12345.jpg",
  "notes": "Lunch with Acme Corp representatives to discuss contract renewal",
  "status": "pending"
}
```

**Response:**
```json
{
  "success": true,
  "expense_id": "EXP-2023-050",
  "message": "Expense submitted for approval"
}
```

### B. Update Expense (`PATCH /api/v1/expenses/{id}`)
**Request:**
```json
{
  "description": "Updated description",
  "amount": 150.00
}
```

### C. Get Expense (for edit) (`GET /api/v1/expenses/{id}`)
**Response:**
```json
{
  "expense_id": "EXP-2023-001",
  "date": "2023-10-29",
  "description": "Office Supplies",
  "category_id": 1,
  "category_name": "Office",
  "amount": 450.00,
  "payment_method": "Corporate Card",
  "receipt_url": "/uploads/receipts/receipt_001.jpg",
  "notes": "Monthly office supplies order",
  "status": "pending",
  "submitted_by": "John Doe",
  "submitted_at": "2023-10-29T10:30:00Z"
}
```

### D. Upload Receipt (`POST /api/v1/uploads`)
**Request:** `multipart/form-data` with file
**Response:**
```json
{
  "success": true,
  "file_url": "/uploads/receipts/receipt_12345.jpg"
}
```

## 4. Logical Actions
- **Cancel**: Returns to `expenses_list.html` without saving.
- **Save Draft**: Saves expense with status "draft".
- **Submit**: Saves expense with status "pending" and triggers approval workflow.
- **Receipt Preview**: Clicking uploaded receipt shows preview modal.
- **Form Validation**: Required fields - Date, Description, Category, Amount.

## 5. Integration Notes
- Linked from Expenses List via "Add Expense" button.
- Edit mode: Pre-populates form when `id` query param present.
- Uses standard form styles from `main.css`.
