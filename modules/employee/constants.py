"""
Employee Constants and Enums
"""

from enum import Enum

class EmployeeStatus(Enum):
    ACTIVE = 'ACTIVE'
    SUSPENDED = 'SUSPENDED'
    ARCHIVED = 'ARCHIVED'

class Department(Enum):
    SALES = 'Sales'
    PURCHASING = 'Purchasing'
    INVENTORY = 'Inventory'
    FINANCE = 'Finance'
    HR = 'HR'
    ADMIN = 'Admin'
    IT = 'IT'
