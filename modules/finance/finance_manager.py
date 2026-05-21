"""
Finance Management Module
Handles cash flow, expenses, result calculation (Income Audit), and Accounts Receivable/Payable.
"""

from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from core.database import get_db
from core.logger import get_logger
from modules.security.audit import AuditLogger

logger = get_logger('finance')

class FinanceManager:
    """Manages Financial Operations"""

    @staticmethod
    def add_expense(type: str, category: str, amount: float, description: str, 
                   user_id: int, payment_method: str = 'cash', employee_id: str = None) -> int:
        """Record an operating expense"""
        db = get_db()
        try:
            # Generate Expense ID
            date_str = datetime.now().strftime('%Y%m%d')
            prefix = f"EXP-{date_str}-"
            # Simple cursor query for last id
            row = db.fetch_one("SELECT MAX(id) as max_id FROM expenses")
            new_id_num = (row['max_id'] or 0) + 1
            expense_id = f"{prefix}{new_id_num:04d}"

            record_id = db.insert('expenses', {
                'expense_id': expense_id,
                'expense_date': datetime.now().date().isoformat(),
                'expense_type': type, # fixed/variable
                'category': category,
                'amount': amount,
                'payment_method': payment_method,
                'description': description,
                'payment_method': payment_method,
                'description': description,
                'employee_id': employee_id,
                'created_by': user_id
            })
            
            # Also record in payments table as 'expense'
            db.insert('payments', {
                'payment_type': 'expense',
                'entity_type': 'expense',
                'entity_id': expense_id,
                'amount': amount,
                'payment_date': datetime.now().date().isoformat(),
                'payment_method': payment_method,
                'notes': description,
                'created_by': user_id
            })
            
            AuditLogger.log(user_id, 'ADD_EXPENSE', 'expenses', expense_id, new_value=str(amount))
            return record_id
        except Exception as e:
            logger.error(f"Failed to add expense: {e}")
            raise

    @staticmethod
    def get_cash_flow(start_date: str, end_date: str) -> Dict[str, float]:
        """Calculate Inflows and Outflows for a period based on payments table"""
        db = get_db()
        query = """
            SELECT payment_type, SUM(amount) as total 
            FROM payments 
            WHERE payment_date BETWEEN ? AND ? 
            GROUP BY payment_type
        """
        rows = db.fetch_all(query, (start_date, end_date))
        
        result = {'income': 0.0, 'expense': 0.0}
        for row in rows:
            if row['payment_type'] == 'income':
                result['income'] = row['total']
            else:
                result['expense'] += row['total'] # expenses + supplier payments
        
        result['net_cash_flow'] = result['income'] - result['expense']
        return result

    @staticmethod
    def get_profit_loss(start_date: str, end_date: str) -> Dict[str, float]:
        """
        Calculate P&L based on:
        Revenue (Invoiced Sales) - COGS (Sales Cost) - Operating Expenses
        Verified against dates.
        """
        db = get_db()
        
        # 1. Sales Revenue & COGS (Accrual Basis - based on Invoice Date)
        sales = db.fetch_one("""
            SELECT SUM(total_amount) as revenue, SUM(total_cost) as cogs 
            FROM sales_orders 
            WHERE status IN ('invoiced', 'paid', 'completed') 
            AND order_date BETWEEN ? AND ?
        """, (start_date, end_date))
        
        revenue = sales['revenue'] or 0.0
        cogs = sales['cogs'] or 0.0
        gross_profit = revenue - cogs
        
        # 2. Operating Expenses
        exps = db.fetch_one("""
            SELECT SUM(amount) as total 
            FROM expenses 
            WHERE expense_date BETWEEN ? AND ?
        """, (start_date, end_date))
        
        operating_expenses = exps['total'] or 0.0
        
        net_profit = gross_profit - operating_expenses
        
        return {
            'revenue': revenue,
            'cogs': cogs,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'net_profit': net_profit
        }

    @staticmethod
    def get_accounts_receivable() -> float:
        """Total money owed by customers"""
        db = get_db()
        # Sum of positive balances (assuming positive balance = owed to us, depends on implementation)
        # In SalesManager: 
        # Generate Invoice -> new_balance = old_balance + order_amount (Balance increases)
        # Payment -> new_balance = old_balance - payment
        # So Positive Balance = Customer Owes Us.
        row = db.fetch_one("SELECT SUM(current_balance) as total FROM customers WHERE current_balance > 0")
        return row['total'] or 0.0

    @staticmethod
    def get_accounts_payable() -> float:
        """Total money owed to suppliers"""
        db = get_db()
        # In PurchasingManager:
        # Receipt -> balance increases
        # Payment -> balance decreases
        # So Positive Balance = We Owe Supplier.
        row = db.fetch_one("SELECT SUM(current_balance) as total FROM suppliers WHERE current_balance > 0")
        return row['total'] or 0.0
