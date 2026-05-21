"""
Accounting Service
Double-entry bookkeeping implementation with workflow integration
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
from core.database import get_db, DatabaseError
from core.logger import get_logger
from core.validators import ValidationError
from modules.workflow.service import WorkflowService
from modules.security.audit import AuditLogger

logger = get_logger('accounting')


class AccountingService:
    """Manages accounting operations with double-entry bookkeeping"""
    
    @staticmethod
    def create_journal_entry(entry_date: date, description: str, lines: List[Dict],
                           reference: str = None, user_id: int = None) -> str:
        """
        Create a journal entry (unposted).
        
        Args:
            entry_date: Transaction date
            description: Entry description
            lines: List of {'account_id': str, 'debit': float, 'credit': float, 'description': str}
            reference: Optional reference number
            user_id: Creating user
        
        Returns:
            entry_id
        
        Raises:
            ValidationError: If debits != credits or invalid accounts
        """
        # Validate double-entry
        total_debits = sum(Decimal(str(line.get('debit', 0))) for line in lines)
        total_credits = sum(Decimal(str(line.get('credit', 0))) for line in lines)
        
        if total_debits != total_credits:
            raise ValidationError(
                f"Debits ({total_debits}) must equal Credits ({total_credits})"
            )
        
        if total_debits == 0:
            raise ValidationError("Journal entry must have non-zero amounts")
        
        db = get_db()
        
        try:
            with db.transaction():
                # Generate entry ID
                date_str = entry_date.strftime('%Y%m%d')
                row = db.fetch_one("SELECT MAX(id) as max_id FROM journal_entries")
                new_id_num = (row['max_id'] or 0) + 1
                entry_id = f"JE-{date_str}-{new_id_num:04d}"
                
                # Create journal entry header
                db.insert('journal_entries', {
                    'entry_id': entry_id,
                    'entry_date': entry_date.isoformat(),
                    'description': description,
                    'reference': reference,
                    'is_posted': 0,
                    'created_by': user_id,
                    'created_at': datetime.now()
                })
                
                # Create ledger lines
                for line in lines:
                    # Validate account exists
                    account = db.fetch_one(
                        "SELECT account_id FROM accounts WHERE account_id=?",
                        (line['account_id'],)
                    )
                    if not account:
                        raise ValidationError(f"Invalid account: {line['account_id']}")
                    
                    debit = Decimal(str(line.get('debit', 0)))
                    credit = Decimal(str(line.get('credit', 0)))
                    
                    if debit > 0 and credit > 0:
                        raise ValidationError("Line cannot have both debit and credit")
                    
                    db.insert('ledger_entries', {
                        'journal_entry_id': entry_id,
                        'account_id': line['account_id'],
                        'debit_amount': float(debit),
                        'credit_amount': float(credit),
                        'description': line.get('description', description)
                    })
                
                # Initialize workflow
                WorkflowService.initialize_document_state('JOURNAL_ENTRY', entry_id)
                
                AuditLogger.log(user_id, 'CREATE_JOURNAL', 'journal_entries', entry_id,
                              new_value=f"Dr:{total_debits} Cr:{total_credits}")
                
                logger.info(f"Created journal entry {entry_id}")
                return entry_id
                
        except Exception as e:
            logger.error(f"Failed to create journal entry: {e}")
            raise
    
    @staticmethod
    def post_journal(entry_id: str, user_id: int) -> bool:
        """
        Post journal entry (make immutable and update balances).
        
        Args:
            entry_id: Journal entry ID
            user_id: Posting user
        
        Returns:
            True if successful
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Check if already posted
                entry = db.fetch_one(
                    "SELECT is_posted FROM journal_entries WHERE entry_id=?",
                    (entry_id,)
                )
                
                if not entry:
                    raise ValidationError(f"Journal entry {entry_id} not found")
                
                if entry['is_posted']:
                    raise ValidationError(f"Journal entry {entry_id} already posted")
                
                # Mark as posted
                db.update('journal_entries', {
                    'is_posted': 1,
                    'posted_date': datetime.now().date().isoformat(),
                    'posted_by': user_id
                }, 'entry_id = ?', (entry_id,))
                
                # Update account balances (could maintain running balance table)
                # For now, balances are calculated on-demand
                
                AuditLogger.log(user_id, 'POST_JOURNAL', 'journal_entries', entry_id)
                logger.info(f"Posted journal entry {entry_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to post journal {entry_id}: {e}")
            raise
    
    @staticmethod
    def reverse_journal(entry_id: str, reversal_date: date, user_id: int) -> str:
        """
        Create a reversing journal entry.
        
        Args:
            entry_id: Original entry to reverse
            reversal_date: Date of reversal
            user_id: User performing reversal
        
        Returns:
            New (reversing) entry_id
        """
        db = get_db()
        
        # Get original entry
        original = db.fetch_one(
            "SELECT * FROM journal_entries WHERE entry_id=?",
            (entry_id,)
        )
        
        if not original:
            raise ValidationError(f"Journal entry {entry_id} not found")
        
        if not original['is_posted']:
            raise ValidationError("Cannot reverse unposted entry")
        
        # Get original lines
        lines = db.fetch_all(
            "SELECT * FROM ledger_entries WHERE journal_entry_id=?",
            (entry_id,)
        )
        
        # Create reversing lines (swap debit/credit)
        reversing_lines = []
        for line in lines:
            reversing_lines.append({
                'account_id': line['account_id'],
                'debit': line['credit_amount'],  # Swap
                'credit': line['debit_amount'],  # Swap
                'description': line['description']
            })
        
        # Create new entry
        new_entry_id = AccountingService.create_journal_entry(
            entry_date=reversal_date,
            description=f"REVERSAL: {original['description']}",
            lines=reversing_lines,
            reference=entry_id,
            user_id=user_id
        )
        
        # Auto-post reversing entry
        AccountingService.post_journal(new_entry_id, user_id)
        
        logger.info(f"Reversed entry {entry_id} with {new_entry_id}")
        return new_entry_id
    
    @staticmethod
    def get_general_ledger(account_id: str = None, start_date: date = None,
                          end_date: date = None, posted_only: bool = True) -> List[Dict]:
        """
        Get general ledger entries.
        
        Args:
            account_id: Filter by account (None = all)
            start_date: Start date filter
            end_date: End date filter
            posted_only: Only posted entries
        
        Returns:
            List of ledger entries with running balance
        """
        db = get_db()
        
        sql = """
            SELECT 
                le.*,
                je.entry_date,
                je.description as entry_description,
                je.is_posted,
                a.account_number,
                a.account_name,
                a.account_type
            FROM ledger_entries le
            JOIN journal_entries je ON le.journal_entry_id = je.entry_id
            JOIN accounts a ON le.account_id = a.account_id
            WHERE 1=1
        """
        
        params = []
        
        if account_id:
            sql += " AND le.account_id = ?"
            params.append(account_id)
        
        if start_date:
            sql += " AND je.entry_date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            sql += " AND je.entry_date <= ?"
            params.append(end_date.isoformat())
        
        if posted_only:
            sql += " AND je.is_posted = 1"
        
        sql += " ORDER BY je.entry_date, le.entry_line_id"
        
        entries = db.fetch_all(sql, tuple(params))
        
        # Calculate running balance
        balance = Decimal('0')
        result = []
        
        for entry in entries:
            debit = Decimal(str(entry['debit_amount']))
            credit = Decimal(str(entry['credit_amount']))
            
            # Normal balance direction depends on account type
            account_type = entry['account_type']
            if account_type in ['ASSET', 'EXPENSE']:
                balance += debit - credit
            else:  # LIABILITY, EQUITY, REVENUE
                balance += credit - debit
            
            result.append({
                **dict(entry),
                'balance': float(balance)
            })
        
        return result
    
    @staticmethod
    def get_trial_balance(as_of_date: date = None) -> Dict[str, Dict]:
        """
        Get trial balance (all accounts with debit/credit totals).
        
        Args:
            as_of_date: Balance as of this date (None = all time)
        
        Returns:
            Dict of {account_id: {'account_name', 'debit', 'credit', 'balance'}}
        """
        db = get_db()
        
        sql = """
            SELECT 
                a.account_id,
                a.account_number,
                a.account_name,
                a.account_type,
                COALESCE(SUM(le.debit_amount), 0) as total_debit,
                COALESCE(SUM(le.credit_amount), 0) as total_credit
            FROM accounts a
            LEFT JOIN ledger_entries le ON a.account_id = le.account_id
            LEFT JOIN journal_entries je ON le.journal_entry_id = je.entry_id
            WHERE je.is_posted = 1
        """
        
        params = []
        if as_of_date:
            sql += " AND je.entry_date <= ?"
            params.append(as_of_date.isoformat())
        
        sql += " GROUP BY a.account_id ORDER BY a.account_number"
        
        accounts = db.fetch_all(sql, tuple(params))
        
        result = {}
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for acc in accounts:
            debit = Decimal(str(acc['total_debit']))
            credit = Decimal(str(acc['total_credit']))
            
            # Net balance (normal balance side)
            if acc['account_type'] in ['ASSET', 'EXPENSE']:
                balance = debit - credit
            else:
                balance = credit - debit
            
            result[acc['account_id']] = {
                'account_number': acc['account_number'],
                'account_name': acc['account_name'],
                'account_type': acc['account_type'],
                'debit': float(debit),
                'credit': float(credit),
                'balance': float(balance)
            }
            
            total_debits += debit
            total_credits += credit
        
        # Verify trial balance
        if total_debits != total_credits:
            logger.warning(f"Trial balance out of balance! Dr:{total_debits} Cr:{total_credits}")
        
        result['_totals'] = {
            'total_debit': float(total_debits),
            'total_credit': float(total_credits),
            'in_balance': total_debits == total_credits
        }
        
        return result
    
    @staticmethod
    def close_period(period_end_date: date, user_id: int) -> str:
        """
        Close accounting period (close revenue/expense to retained earnings).
        
        Args:
            period_end_date: End of period
            user_id: User performing close
        
        Returns:
            Closing entry_id
        """
        db = get_db()
        
        # Calculate net income (Revenue - Expenses)
        revenue_sql = """
            SELECT COALESCE(SUM(le.credit_amount - le.debit_amount), 0) as total
            FROM ledger_entries le
            JOIN journal_entries je ON le.journal_entry_id = je.entry_id
            JOIN accounts a ON le.account_id = a.account_id
            WHERE a.account_type = 'REVENUE' AND je.is_posted = 1
            AND je.entry_date <= ?
        """
        
        expense_sql = """
            SELECT COALESCE(SUM(le.debit_amount - le.credit_amount), 0) as total
            FROM ledger_entries le
            JOIN journal_entries je ON le.journal_entry_id = je.entry_id
            JOIN accounts a ON le.account_id = a.account_id
            WHERE a.account_type = 'EXPENSE' AND je.is_posted = 1
            AND je.entry_date <= ?
        """
        
        revenue = db.fetch_one(revenue_sql, (period_end_date.isoformat(),))['total']
        expense = db.fetch_one(expense_sql, (period_end_date.isoformat(),))['total']
        
        net_income = Decimal(str(revenue)) - Decimal(str(expense))
        
        # Get retained earnings account
        re_account = db.fetch_one(
            "SELECT account_id FROM accounts WHERE account_number=?",
            ('3020',)  # Retained Earnings
        )
        
        if not re_account:
            raise ValidationError("Retained Earnings account not found")
        
        # Create closing entry
        closing_lines = []
        
        if net_income > 0:
            # Net income: Dr Revenue, Cr Retained Earnings
            closing_lines.append({
                'account_id': '4010',  # Revenue
                'debit': float(net_income),
                'credit': 0,
                'description': 'Close revenue to RE'
            })
            closing_lines.append({
                'account_id': re_account['account_id'],
                'debit': 0,
                'credit': float(net_income),
                'description': 'Net income transfer'
            })
        elif net_income < 0:
            # Net loss: Dr Retained Earnings, Cr Expense
            closing_lines.append({
                'account_id': re_account['account_id'],
                'debit': float(abs(net_income)),
                'credit': 0,
                'description': 'Net loss transfer'
            })
            closing_lines.append({
                'account_id': '6010',  # Expense
                'debit': 0,
                'credit': float(abs(net_income)),
                'description': 'Close expenses to RE'
            })
        
        if not closing_lines:
            logger.info("No closing entry needed (net income = 0)")
            return None
        
        entry_id = AccountingService.create_journal_entry(
            entry_date=period_end_date,
            description=f"Period Closing: Net Income ${net_income}",
            lines=closing_lines,
            reference=f"CLOSE-{period_end_date.isoformat()}",
            user_id=user_id
        )
        
        # Auto-post
        AccountingService.post_journal(entry_id, user_id)
        
        logger.info(f"Period closed with entry {entry_id}, Net Income: ${net_income}")
        return entry_id
