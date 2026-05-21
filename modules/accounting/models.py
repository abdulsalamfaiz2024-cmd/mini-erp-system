"""
Accounting Models
Double-entry bookkeeping structures
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import date


@dataclass
class Account:
    """Chart of Accounts entry"""
    account_id: str
    account_number: str
    account_name: str
    account_type: str  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    parent_account_id: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None


@dataclass
class JournalEntry:
    """Journal Entry header"""
    entry_id: str
    entry_date: date
    description: str
    reference: Optional[str] = None
    is_posted: bool = False
    posted_date: Optional[date] = None
    created_by: int = None
    posted_by: Optional[int] = None


@dataclass
class LedgerEntry:
    """Individual debit/credit line in journal"""
    entry_line_id: int
    journal_entry_id: str
    account_id: str
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    description: Optional[str] = None
    
    @property
    def is_debit(self) -> bool:
        return self.debit_amount > 0
    
    @property
    def is_credit(self) -> bool:
        return self.credit_amount > 0


# Account type constants
class AccountType:
    ASSET = 'ASSET'
    LIABILITY = 'LIABILITY'
    EQUITY = 'EQUITY'
    REVENUE = 'REVENUE'
    EXPENSE = 'EXPENSE'


# Standard account numbers
class StandardAccounts:
    """Common account number structure"""
    CASH = '1010'
    ACCOUNTS_RECEIVABLE = '1020'
    INVENTORY = '1030'
    ACCOUNTS_PAYABLE = '2010'
    EQUITY = '3010'
    RETAINED_EARNINGS = '3020'
    SALES_REVENUE = '4010'
    COST_OF_GOODS_SOLD = '5010'
    OPERATING_EXPENSES = '6010'
