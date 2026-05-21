# Plan 1.2: Database Architecture & Core Models (Exhaustive Detail)

## 1. Scope & Objective
This document defines the data persistence strategy for the entire Apex ERP. It ensures that every table follows a standardized structure for auditing, indexing, and relational integrity.

---

## 2. The Global "Base" Architecture
Every model in the system MUST inherit from a centralized `Base` class. This class will include "Global Mixins" to ensure we track the lifecycle of every piece of data.

### Standardized Fields (Shared Mixin)
Every table from "Customers" to "Journal Entries" will automatically contain:
- `id` (UUID): A globally unique identifier to prevent ID guessing and collisions.
- `created_at` (TIMESTAMP): Set once upon creation.
- `updated_at` (TIMESTAMP): Updated every time the row is modified.
- `is_active` (BOOLEAN): Used for "Soft Deletes" to prevent data loss.

---

## 3. Database Connection Protocol (`database.py`)
The engine must be configured with specific parameters to handle the high concurrency of an ERP system.

| Parameter | Value | Justification |
| :--- | :--- | :--- |
| **pool_size** | 20 | Maintain 20 active connections to handle simultaneous requests. |
| **max_overflow** | 10 | Allow up to 10 additional connections during peak traffic (e.g., month-end reporting). |
| **pool_pre_ping** | True | Verify the connection is alive before handing it to a process, preventing "stale connection" errors. |
| **autocommit** | False | Transactions must be manually committed to ensure atomicity. |

---

## 4. Key Implementation Details: `models/base.py`
```python
from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class ERPBase:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

---

## 5. Mapping the Specific Modules
This phase prepares for Phase 2 by defining the "Reserved Table Names" in the database to prevent naming conflicts.

- **Finance**: `fin_ledgers`, `fin_expenses`, `fin_journals`.
- **Sales**: `sls_orders`, `sls_order_items`, `sls_invoices`.
- **Inventory**: `inv_products`, `inv_stock_history`, `inv_warehouses`.
- **Purchasing**: `pur_orders`, `pur_suppliers`.

---

## 6. Verification Steps (The "Schema-Check" Protocol)
Before proceeding to Step 1.3:
1. [ ] **Connection Verification**: Run a standalone script to connect to PostgreSQL and print "Connection Successful".
2. [ ] **Base Class Integrity**: Verify that importing `Base` does not trigger circular dependency errors.
3. [ ] **Automatic Migration Setup**: Initialize `Alembic` (Database migration tool) to track schema changes.
4. [ ] **Audit Trail Confirmation**: Verify that all `ERPBase` fields are present in the generated SQL.
