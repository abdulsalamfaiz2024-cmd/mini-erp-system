# Mini-ERP Sales and Inventory Management System

A desktop business application that handles sales transactions, inventory valuation, and basic financial reporting. Built with Python and Tkinter, the system is designed to provide small businesses with a fast, lightweight tool for managing their operations without the overhead of heavy web-based ERP frameworks.

## Core Features

- **Sales Management**: Simplified checkout workflow, billing, and real-time transaction processing.
- **Inventory Control**: First-in, first-out (FIFO) inventory cost tracking, low-stock alerts, and multi-batch organization.
- **Financial Reporting**: Generates automated Profit & Loss statements, cash flow logs, and Accounts Receivable/Payable reports.
- **Performance Optimizations**: Implemented local query caching and transaction buffering to optimize database performance.
- **Productivity Utilities**: Global keyboard search shortcuts (Ctrl+K), PDF invoice generation, and custom report exports to CSV/Excel.

## Technical Stack

- **Language**: Python 3.12
- **UI Framework**: Tkinter (with ttk styling)
- **Database**: SQLite (with WAL mode enabled)
- **Reporting**: ReportLab (PDF) and openpyxl/pandas (Excel)
- **Security**: PBKDF2-HMAC-SHA256 for password hashing and role-based permissions

## Getting Started

### Installation

1. Navigate to the project directory:
   ```bash
   cd sales_systems
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the application:
   ```bash
   python run_erp.py
   ```

### Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Testing

Run the automated test suite to verify application logic:

```bash
python -m pytest tests/test_comprehensive.py -v
```
