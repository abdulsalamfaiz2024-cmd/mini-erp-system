# Plan 1.4: Global Database Schema & Entity Relationships

## 1. Scope & Objective
This document serves as the absolute master blueprint for the Apex ERP Database. It defines the tables, columns, data types, and the complex web of relationships (Foreign Keys) that ensure data integrity across modules.

---

## 2. Global Conventions
- **Naming**: All tables use snake_case and are prefixed by their module (e.g., `sls_` for Sales).
- **Primary Keys**: All tables use `UUID` (Universally Unique Identifier) as defined in Plan 1.2.
- **Foreign Keys**: Must have `ON DELETE RESTRICT` to prevent accidental deletion of critical history.

---

## 3. Core Tables & Relationship Map

### 3.1. Master Data (The Anchors)
| Table | Module | Primary Columns | Relationships |
| :--- | :--- | :--- | :--- |
| `mst_users` | Security | `username`, `hashed_password`, `role` | Parent to all CreatedBy logs. |
| `mst_customers` | CRM | `name`, `email`, `billing_addr`, `shipping_addr` | Parent to `sls_orders`, `ret_requests`. |
| `mst_suppliers` | Pur. | `company_name`, `contact_name`, `api_endpoint` | Parent to `pur_orders`. |
| `inv_products` | Inv. | `sku`, `name`, `unit_price`, `stock_qty` | Parent to all Order Items and Adjustments. |
| `inv_warehouses`| Inv. | `location_name`, `capacity`, `manager_id` | Parent to `inv_stock_history`. |

### 3.2. Sales & Finance Transactional Linkage
| Table | Module | Primary Columns | Relationships |
| :--- | :--- | :--- | :--- |
| `sls_orders` | Sales | `order_number`, `customer_id`, `status` | FK to `mst_customers`. Parent to `sls_order_items`. |
| `sls_order_items`| Sales | `order_id`, `product_id`, `qty`, `price` | FK to `sls_orders`, `inv_products`. |
| `fin_invoices` | Fin. | `invoice_number`, `order_id`, `total_amount` | FK to `sls_orders`. Links Sales to Finance. |
| `fin_ledger` | Fin. | `transaction_id`, `account_type`, `debit`, `credit` | FK to `fin_invoices` or `fin_expenses`. |

### 3.3. Purchasing & Returns Linkage
| Table | Module | Primary Columns | Relationships |
| :--- | :--- | :--- | :--- |
| `pur_orders` | Pur. | `po_number`, `supplier_id`, `total_cost` | FK to `mst_suppliers`. |
| `ret_requests` | Ret. | `return_id`, `original_order_id`, `reason` | FK to `sls_orders`. |
| `ret_items` | Ret. | `return_id`, `product_id`, `condition_status` | FK to `ret_requests`, `inv_products`. |

---

## 4. Detailed Entity Relationship Diagram (ERD) Logic

### The "Sales-to-Cash" Chain
1. `mst_customers` (1) <---> (N) `sls_orders`
2. `sls_orders` (1) <---> (N) `sls_order_items` (Links to `inv_products`)
3. `sls_orders` (1) <---> (1) `fin_invoices`
4. `fin_invoices` (1) <---> (N) `fin_ledger`

### The "Procure-to-Pay" Chain
1. `mst_suppliers` (1) <---> (N) `pur_orders`
2. `pur_orders` (1) <---> (N) `pur_order_items`
3. `pur_orders` (1) <---> (N) `inv_stock_history` (On Goods Receipt)

---

## 5. Constraint & Integrity Rules
1. **Stock Lock**: A Sales Order cannot be completed if `inv_products.stock_qty < sls_order_items.qty`.
2. **Atomic Ledger**: Any update to `fin_invoices.status = 'Paid'` MUST trigger a background transaction to create matching entries in `fin_ledger` and `fin_journals`.
3. **Audit Trail**: Every transaction table MUST store the `UUID` of the user who performed the action in a `created_by` column.

---

## 6. Verification Steps
1. [ ] **Cross-Spec Audit**: Ensure every key mentioned in the 30 `_spec.md` files has a corresponding column in this schema.
2. [ ] **Circular Dependency Check**: Ensure that table creation order (Migrations) can be executed without FK conflicts.
3. [ ] **Cardinality Check**: Verify all 1:N and M:N relationships are correctly handled via bridge tables if necessary.
