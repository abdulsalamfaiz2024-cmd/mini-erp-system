# Employee Management Module

## Overview
The Employee Management module serves as the foundational identity and permission layer for the ERP system. It manages employee data, operational status, and workflow permissions.

**Key Features:**
- **Immutable Records**: Employees are never deleted, only ARCHIVED.
- **Operational Gating**: Only ACTIVE employees can perform actions.
- **Granular Permissions**: Boolean flags for specific workflows (Orders, Inventory, Accounting).
- **Audit Traceability**: All changes are logged.

## Data Model

### Employee Entity
- **Identity**: `employee_id` (UUID), `full_name`, `job_title`, `department`.
- **Status**: `ACTIVE`, `SUSPENDED`, `ARCHIVED`.
- **Permissions**: `can_create_orders`, `can_approve_orders`, `can_release_inventory`, `can_post_accounting`.
- **Links**: `user_id` (Optional link to Auth User).

## Integration Notes

### 1. Linking to Authentication
The `users` table manages login credentials. The `employees` table manages business identity.
To link them:
```python
# When creating/updating an employee:
EmployeeService.create_employee({
    ...,
    'user_id': authenticated_user_id
})
```
*One-to-One Constraint*: The database schema enforces `UNIQUE(user_id)`.

### 2. Using in Future Modules
When implementing Sales, Inventory, or Finance:

**Authorization Check:**
```python
from modules.employee.service import EmployeeService

emp = EmployeeService.get_employee(current_employee_id)
if not emp.is_active:
    raise PermissionError("Employee is not active")

if not emp.can_create_orders:
    raise PermissionError("Insufficient permissions")
```

**Auditing:**
Pass `employee_id` to audit logs instead of just `user_id` where applicable, or map them.

## Service Usage

```python
from modules.employee.service import EmployeeService

# Create
emp_id = EmployeeService.create_employee({
    'full_name': 'Alice Smith',
    'job_title': 'Sales Manager',
    'department': 'Sales',
    'can_create_orders': True,
    'can_approve_orders': True
})

# Update
EmployeeService.update_employee(emp_id, {'job_title': 'Director'})

# Suspend
EmployeeService.change_status(emp_id, EmployeeStatus.SUSPENDED)
```
