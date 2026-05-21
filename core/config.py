"""
Configuration management for Mini-ERP system
Centralized settings for database, paths, and business rules
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database configuration
DATABASE_CONFIG = {
    'name': 'perfect_sales_system.db',
    'path': BASE_DIR / 'perfect_sales_system.db',
    'backup_dir': BASE_DIR / 'backups',
    'enable_foreign_keys': True,
    'enable_wal_mode': True,  # Write-Ahead Logging for better concurrency
}

# Excel integration configuration
EXCEL_CONFIG = {
    'data_dir': BASE_DIR / 'data',
    'auto_export': True,
    'conflict_resolution': 'database_wins',
    'validate_schema': True,
}

# File mappings (Excel filename -> Database table)
EXCEL_TABLE_MAPPING = {
    'customers.xlsx': 'customers',
    'products.xlsx': 'products',
    'inventory.xlsx': 'inventory',
    'suppliers.xlsx': 'suppliers',
    'sales.xlsx': 'sales_orders',
    'sale_items.xlsx': 'sales_order_items',
    'purchases.xlsx': 'purchase_orders',
    'purchase_items.xlsx': 'purchase_order_items',
    'daily_sales_summary.xlsx': None,  # Report file, not imported
    'data_entry_templates.xlsx': None,  # Template file, not imported
}

# Security configuration
SECURITY_CONFIG = {
    'password_min_length': 8,
    'session_timeout_minutes': 60,
    'max_login_attempts': 5,
    'password_hash_rounds': 12,
}

# Business rules
BUSINESS_RULES = {
    'default_currency': 'SAR',
    'decimal_places': 2,
    'low_stock_threshold': 10,
    'default_payment_terms': 30,  # days
    'enable_negative_stock': False,
    'auto_generate_invoice_numbers': True,
}

# Logging configuration
LOGGING_CONFIG = {
    'log_dir': BASE_DIR / 'logs',
    'log_level': 'INFO',
    'max_log_size_mb': 10,
    'backup_count': 5,
}

# UI configuration
UI_CONFIG = {
    'theme': 'clam',
    'window_size': '1400x900',
    'font_family': 'Arial',
    'font_size': 11,
    'language': 'en',  # Changed to English - was 'ar'
}

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    dirs = [
        DATABASE_CONFIG['backup_dir'],
        EXCEL_CONFIG['data_dir'],
        LOGGING_CONFIG['log_dir'],
    ]
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize on import
ensure_directories()
