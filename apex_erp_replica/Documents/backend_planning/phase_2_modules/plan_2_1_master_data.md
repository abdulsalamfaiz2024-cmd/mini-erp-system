# Plan 2.1: Master Data Management (Exhaustive Detail)

## 1. Scope & Objective
This document defines the implementation details for the system's "Master Data"—the static entities that power all other transactions. This includes Customers, Products, Suppliers, and Warehouses.

---

## 2. Table Specifications & Schema Logic

### 2.1. Customers (`mst_customers`)
- **Source**: `customer_profile_spec.md`
- **Fields**:
    - `id` (UUID, PK)
    - `name` (String, 100)
    - `contact_person` (String, 100)
    - `email` (String, 100, Unique)
    - `phone` (String, 20)
    - `billing_address` (Text)
    - `shipping_address` (Text)
    - `tax_id` (String, 50)
    - `credit_limit` (Decimal, 12, 2)
- **Controller Logic**: `controllers/customer_manager.py`
    - `get_customer_history()`: Aggregates all orders and invoices for a client.

### 2.2. Products (`inv_products`)
- **Source**: `product_list_spec.md`, `product_details_spec.md`
- **Fields**:
    - `sku` (String, 50, Unique)
    - `name` (String, 255)
    - `description` (Text)
    - `category` (String, 50)
    - `unit_price` (Decimal, 12, 2)
    - `cost_price` (Decimal, 12, 2)
    - `stock_qty` (Integer)
    - `reorder_level` (Integer)
- **Controller Logic**: `controllers/inventory_manager.py`
    - `check_stock_availability(sku, requested_qty)`: Boolean check before sales order submission.

---

## 3. API Contract Layer (Pydantic Schemas)
Located in `Backend/schemas/master_data.py`.

```python
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    billing_address: str
    shipping_address: Optional[str] = None
    # ... other fields
```

---

## 4. Logical Interconnections
- **Search**: Every master data controller must implement a "Global Search" function using PostgreSQL `ILIKE` or `tsvector` for the frontend's search bars.
- **Validation**: Cannot delete a Customer if they have an active `sls_order`.

---

## 5. Verification Steps
1. [ ] **CRUD Functional Test**: Verify Create, Read, Update, Delete for all 4 entities via Swagger.
2. [ ] **Unique Constraint Test**: Attempt to create a Product with an existing SKU; verify 400 error.
3. [ ] **JSON Mapping**: Verify that the backend response keys match exactly what the frontend Expects in `customer_profile_spec.md`.
