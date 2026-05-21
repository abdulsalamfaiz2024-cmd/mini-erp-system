"""
Data validation utilities for Mini-ERP
Provides validators for forms, business rules, and data types
"""

import re
from datetime import datetime
from typing import Any, Optional, List
from decimal import Decimal, InvalidOperation

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class Validator:
    """Base validator class"""
    
    @staticmethod
    def required(value: Any, field_name: str = "Field") -> Any:
        """Validate that a value is not empty"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise ValidationError(f"{field_name} is required")
        return value
    
    @staticmethod
    def min_length(value: str, min_len: int, field_name: str = "Field") -> str:
        """Validate minimum string length"""
        if len(value) < min_len:
            raise ValidationError(f"{field_name} must be at least {min_len} characters")
        return value
    
    @staticmethod
    def max_length(value: str, max_len: int, field_name: str = "Field") -> str:
        """Validate maximum string length"""
        if len(value) > max_len:
            raise ValidationError(f"{field_name} must not exceed {max_len} characters")
        return value
    
    @staticmethod
    def email(value: str, field_name: str = "Email") -> str:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValidationError(f"{field_name} is not a valid email address")
        return value
    
    @staticmethod
    def phone(value: str, field_name: str = "Phone") -> str:
        """Validate phone number (Saudi format)"""
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-]', '', value)
        # Saudi phone: starts with 05 or +9665, followed by 8 digits
        pattern = r'^(05\d{8}|(\+9665|9665)\d{8})$'
        if not re.match(pattern, cleaned):
            raise ValidationError(f"{field_name} is not a valid phone number")
        return value
    
    @staticmethod
    def positive_number(value: Any, field_name: str = "Value") -> float:
        """Validate positive number"""
        try:
            num = float(value)
            if num <= 0:
                raise ValidationError(f"{field_name} must be a positive number")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number")
    
    @staticmethod
    def non_negative_number(value: Any, field_name: str = "Value") -> float:
        """Validate non-negative number"""
        try:
            num = float(value)
            if num < 0:
                raise ValidationError(f"{field_name} cannot be negative")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid number")
    
    @staticmethod
    def integer(value: Any, field_name: str = "Value") -> int:
        """Validate integer"""
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")
    
    @staticmethod
    def positive_integer(value: Any, field_name: str = "Value") -> int:
        """Validate positive integer"""
        try:
            num = int(value)
            if num <= 0:
                raise ValidationError(f"{field_name} must be a positive integer")
            return num
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")
    
    @staticmethod
    def date(value: Any, field_name: str = "Date", format: str = "%Y-%m-%d") -> datetime:
        """Validate date format"""
        if isinstance(value, datetime):
            return value
        try:
            return datetime.strptime(value, format)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid date in format {format}")
    
    @staticmethod
    def in_list(value: Any, valid_values: List[Any], field_name: str = "Value") -> Any:
        """Validate value is in allowed list"""
        if value not in valid_values:
            raise ValidationError(f"{field_name} must be one of: {', '.join(map(str, valid_values))}")
        return value
    
    @staticmethod
    def decimal_places(value: Any, places: int, field_name: str = "Value") -> Decimal:
        """Validate decimal places"""
        try:
            dec = Decimal(str(value))
            # Round to specified decimal places
            quantizer = Decimal(10) ** -places
            return dec.quantize(quantizer)
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid decimal number")

class BusinessValidator:
    """Business rule validators"""
    
    @staticmethod
    def stock_availability(product_id: str, requested_qty: int, available_qty: int) -> bool:
        """Validate stock availability"""
        if requested_qty > available_qty:
            raise ValidationError(
                f"Insufficient stock for product {product_id}. "
                f"Requested: {requested_qty}, Available: {available_qty}"
            )
        return True
    
    @staticmethod
    def credit_limit(customer_id: str, current_balance: float, 
                     new_amount: float, credit_limit: float) -> bool:
        """Validate customer credit limit"""
        total_balance = current_balance + new_amount
        if total_balance > credit_limit:
            raise ValidationError(
                f"Credit limit exceeded for customer {customer_id}. "
                f"Limit: {credit_limit}, Would be: {total_balance}"
            )
        return True
    
    @staticmethod
    def payment_amount(invoice_total: float, paid_amount: float, 
                       payment_amount: float) -> bool:
        """Validate payment amount doesn't exceed remaining balance"""
        remaining = invoice_total - paid_amount
        if payment_amount > remaining:
            raise ValidationError(
                f"Payment amount ({payment_amount}) exceeds remaining balance ({remaining})"
            )
        return True
    
    @staticmethod
    def date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range"""
        if end_date < start_date:
            raise ValidationError("End date cannot be before start date")
        return True
    
    @staticmethod
    def unique_invoice_number(invoice_number: str, existing_numbers: List[str]) -> bool:
        """Validate invoice number is unique"""
        if invoice_number in existing_numbers:
            raise ValidationError(f"Invoice number {invoice_number} already exists")
        return True

def validate_form_data(data: dict, rules: dict) -> dict:
    """
    Validate form data against rules
    
    Args:
        data: Dictionary of field values
        rules: Dictionary of validation rules per field
        
    Returns:
        Validated and cleaned data
        
    Example:
        rules = {
            'name': [('required',), ('min_length', 3)],
            'email': [('required',), ('email',)],
            'quantity': [('required',), ('positive_integer',)]
        }
    """
    validated_data = {}
    errors = {}
    
    for field, field_rules in rules.items():
        value = data.get(field)
        
        try:
            for rule in field_rules:
                if isinstance(rule, tuple):
                    validator_name, *args = rule
                else:
                    validator_name = rule
                    args = []
                
                validator = getattr(Validator, validator_name)
                value = validator(value, field, *args)
            
            validated_data[field] = value
            
        except ValidationError as e:
            errors[field] = str(e)
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return validated_data
