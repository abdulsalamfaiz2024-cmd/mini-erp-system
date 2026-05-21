"""
Tests for Employee Module
"""

import pytest
from core.database import get_db
from modules.employee.service import EmployeeService
from modules.employee.constants import EmployeeStatus
from modules.employee.models import Employee

class TestEmployeeModule:
    
    def test_create_employee(self, test_db):
        """Test creating a new employee"""
        data = {
            'full_name': 'John Doe',
            'job_title': 'Senior Developer',
            'department': 'IT',
            'contact_email': 'john@example.com',
            'can_create_orders': True
        }
        
        emp_id = EmployeeService.create_employee(data)
        assert emp_id is not None
        
        # specific_fetch
        emp = EmployeeService.get_employee(emp_id)
        assert emp.full_name == 'John Doe'
        assert emp.status == EmployeeStatus.ACTIVE
        assert emp.can_create_orders is True
        assert emp.can_approve_orders is False # Default

    def test_update_employee(self, test_db):
        """Test updating employee details"""
        data = {
            'full_name': 'Jane Doe',
            'job_title': 'Manager',
            'department': 'Sales'
        }
        emp_id = EmployeeService.create_employee(data)
        
        update_data = {'job_title': 'Director', 'department': 'Marketing'} # Marketing not in Enum but string allowed in DB
        success = EmployeeService.update_employee(emp_id, update_data)
        assert success is True
        
        emp = EmployeeService.get_employee(emp_id)
        assert emp.job_title == 'Director'
        assert emp.department == 'Marketing'

    def test_archived_employee_immutable(self, test_db):
        """Test that ARCHIVED employees cannot be updated"""
        data = {'full_name': 'Old Guy', 'job_title': 'Retired', 'department': 'Admin'}
        emp_id = EmployeeService.create_employee(data)
        
        EmployeeService.change_status(emp_id, EmployeeStatus.ARCHIVED)
        
        with pytest.raises(Exception): # ValidationError
            EmployeeService.update_employee(emp_id, {'full_name': 'New Name'})

    def test_permissions_assignment(self, test_db):
        """Test permission assignment"""
        data = {'full_name': 'Operator', 'job_title': 'Ops', 'department': 'Ops'}
        emp_id = EmployeeService.create_employee(data)
        
        EmployeeService.assign_permissions(emp_id, {'can_approve_orders': True})
        
        emp = EmployeeService.get_employee(emp_id)
        assert emp.can_approve_orders is True
        
        # Test inactive employee permissions
        EmployeeService.change_status(emp_id, EmployeeStatus.SUSPENDED)
        with pytest.raises(Exception):
            EmployeeService.assign_permissions(emp_id, {'can_approve_orders': False})

    def test_list_employees(self, test_db):
        """Test listing employees"""
        data1 = {'full_name': 'Emp 1', 'job_title': 'J1', 'department': 'D1'}
        data2 = {'full_name': 'Emp 2', 'job_title': 'J2', 'department': 'D2'}
        
        EmployeeService.create_employee(data1)
        id2 = EmployeeService.create_employee(data2)
        EmployeeService.change_status(id2, EmployeeStatus.SUSPENDED)
        
        active = EmployeeService.list_employees(active_only=True)
        all_emps = EmployeeService.list_employees(active_only=False)
        
        assert len(active) >= 1
        assert len(all_emps) >= 2
