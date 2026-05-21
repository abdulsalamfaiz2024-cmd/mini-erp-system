"""
Assets Service
Fixed assets management with depreciation and accounting integration
"""

from typing import List, Dict
from datetime import datetime, date
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from core.database import get_db
from core.logger import get_logger
from core.validators import ValidationError
from modules.security.audit import AuditLogger

logger = get_logger('assets')


class AssetService:
    """Manages fixed assets and depreciation"""
    
    @staticmethod
    def register_asset(asset_name: str, asset_category: str, purchase_date: date,
                      cost: float, salvage_value: float, useful_life_years: int,
                      depreciation_method: str = 'straight_line',
                      user_id: int = None) -> str:
        """
        Register a new fixed asset and generate depreciation schedule.
        
        Args:
            asset_name: Asset description
            asset_category: Category (Vehicle, Equipment, etc)
            purchase_date: Acquisition date
            cost: Purchase cost
            salvage_value: Residual value
            useful_life_years: Useful life in years
            depreciation_method: 'straight_line' or 'declining_balance'
            user_id: User ID
        
        Returns:
            asset_id
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Generate asset ID
                date_str = purchase_date.strftime('%Y%m%d')
                row = db.fetch_one("SELECT MAX(id) as max_id FROM assets")
                new_id_num = (row['max_id'] or 0) + 1
                asset_id = f"AST-{date_str}-{new_id_num:04d}"
                
                # Create asset
                db.insert('assets', {
                    'asset_id': asset_id,
                    'asset_name': asset_name,
                    'asset_category': asset_category,
                    'purchase_date': purchase_date.isoformat(),
                    'cost': cost,
                    'salvage_value': salvage_value,
                    'useful_life_years': useful_life_years,
                    'depreciation_method': depreciation_method,
                    'accumulated_depreciation': 0,
                    'status': 'active',
                    'created_by': user_id
                })
                
                # Generate depreciation schedule
                depreciable_amount = Decimal(str(cost)) - Decimal(str(salvage_value))
                annual_depreciation = depreciable_amount / Decimal(str(useful_life_years))
                
                for year in range(useful_life_years):
                    period_end = purchase_date + relativedelta(years=year+1)
                    
                    db.insert('depreciation_schedules', {
                        'asset_id': asset_id,
                        'period_year': period_end.year,
                        'period_end_date': period_end.isoformat(),
                        'depreciation_amount': float(annual_depreciation),
                        'accumulated_depreciation': float(annual_depreciation * (year + 1)),
                        'book_value': cost - float(annual_depreciation * (year + 1)),
                        'is_posted': 0
                    })
                
                # Create acquisition accounting entry
                try:
                    from modules.accounting.service import AccountingService
                    lines = [
                        {'account_id': '1040', 'debit': cost, 'credit': 0, 'description': f'Asset acquisition: {asset_name}'},  # Fixed Assets
                        {'account_id': '1010', 'debit': 0, 'credit': cost, 'description': f'Cash payment'}  # Cash
                    ]
                    journal_id = AccountingService.create_journal_entry(
                        entry_date=purchase_date,
                        description=f"Asset Acquisition: {asset_name}",
                        lines=lines,
                        reference=asset_id,
                        user_id=user_id
                    )
                    AccountingService.post_journal(journal_id, user_id)
                    logger.info(f"Created acquisition entry {journal_id}")
                except ImportError:
                    logger.warning("Accounting module not available")
                
                AuditLogger.log(user_id, 'REGISTER_ASSET', 'assets', asset_id,
                              new_value=f"Cost:{cost}, Life:{useful_life_years}y")
                
                logger.info(f"Registered asset {asset_id}")
                return asset_id
                
        except Exception as e:
            logger.error(f"Failed to register asset: {e}")
            raise
    
    @staticmethod
    def depreciate_asset(asset_id: str, period_end_date: date, user_id: int):
        """
        Record depreciation for a period.
        
        Args:
            asset_id: Asset ID
            period_end_date: End of depreciation period
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Get asset
                asset = db.fetch_one("SELECT * FROM assets WHERE asset_id=?", (asset_id,))
                if not asset:
                    raise ValidationError(f"Asset {asset_id} not found")
                
                # Get depreciation schedule for period
                schedule = db.fetch_one(
                    "SELECT * FROM depreciation_schedules WHERE asset_id=? AND period_end_date=? AND is_posted=0",
                    (asset_id, period_end_date.isoformat())
                )
                
                if not schedule:
                    raise ValidationError(f"No depreciation schedule found for period {period_end_date}")
                
                depreciation_amount = Decimal(str(schedule['depreciation_amount']))
                
                # Update accumulated depreciation on asset
                new_accumulated = Decimal(str(asset['accumulated_depreciation'])) + depreciation_amount
                db.update('assets', {
                    'accumulated_depreciation': float(new_accumulated)
                }, 'asset_id=?', (asset_id,))
                
                # Mark schedule as posted
                db.update('depreciation_schedules', {
                    'is_posted': 1,
                    'posted_date': datetime.now().date().isoformat()
                }, 'id=?', (schedule['id'],))
                
                # Create accounting entry
                try:
                    from modules.accounting.service import AccountingService
                    lines = [
                        {'account_id': '6020', 'debit': float(depreciation_amount), 'credit': 0, 'description': f'Depreciation: {asset["asset_name"]}'},  # Depreciation Expense
                        {'account_id': '1041', 'debit': 0, 'credit': float(depreciation_amount), 'description': f'Accumulated Depreciation'}  # Accumulated Depreciation
                    ]
                    journal_id = AccountingService.create_journal_entry(
                        entry_date=period_end_date,
                        description=f"Depreciation: {asset['asset_name']}",
                        lines=lines,
                        reference=asset_id,
                        user_id=user_id
                    )
                    AccountingService.post_journal(journal_id, user_id)
                    logger.info(f"Created depreciation entry {journal_id}")
                except ImportError:
                    logger.warning("Accounting module not available")
                
                AuditLogger.log(user_id, 'DEPRECIATE_ASSET', 'assets', asset_id,
                              new_value=f"Amount:{depreciation_amount}")
                
                logger.info(f"Depreciated asset {asset_id} for ${depreciation_amount}")
                
        except Exception as e:
            logger.error(f"Failed to depreciate asset: {e}")
            raise
    
    @staticmethod
    def dispose_asset(asset_id: str, disposal_date: date, disposal_amount: float,
                     user_id: int):
        """
        Dispose of an asset (sale or write-off).
        
        Args:
            asset_id: Asset ID
            disposal_date: Date of disposal
            disposal_amount: Sale proceeds
            user_id: User ID
        """
        db = get_db()
        
        try:
            with db.transaction():
                # Get asset
                asset = db.fetch_one("SELECT * FROM assets WHERE asset_id=?", (asset_id,))
                if not asset:
                    raise ValidationError(f"Asset {asset_id} not found")
                
                cost = Decimal(str(asset['cost']))
                accumulated_dep = Decimal(str(asset['accumulated_depreciation']))
                book_value = cost - accumulated_dep
                disposal_amt = Decimal(str(disposal_amount))
                gain_loss = disposal_amt - book_value
                
                # Update asset status
                db.update('assets', {
                    'status': 'disposed',
                    'disposal_date': disposal_date.isoformat(),
                    'disposal_amount': float(disposal_amt)
                }, 'asset_id=?', (asset_id,))
                
                # Create accounting entry for disposal
                try:
                    from modules.accounting.service import AccountingService
                    lines = [
                        {'account_id': '1010', 'debit': float(disposal_amt), 'credit': 0, 'description': f'Cash from disposal'},  # Cash
                        {'account_id': '1041', 'debit': float(accumulated_dep), 'credit': 0, 'description': f'Remove accumulated depreciation'},  # Accum Dep
                    ]
                    
                    if gain_loss >= 0:
                        # Gain on disposal
                        lines.append({'account_id': '4020', 'debit': 0, 'credit': float(gain_loss), 'description': f'Gain on disposal'})  # Gain
                    else:
                        # Loss on disposal
                        lines.append({'account_id': '6030', 'debit': float(abs(gain_loss)), 'credit': 0, 'description': f'Loss on disposal'})  # Loss
                    
                    lines.append({'account_id': '1040', 'debit': 0, 'credit': float(cost), 'description': f'Remove asset cost'})  # Fixed Assets
                    
                    journal_id = AccountingService.create_journal_entry(
                        entry_date=disposal_date,
                        description=f"Asset Disposal: {asset['asset_name']}",
                        lines=lines,
                        reference=asset_id,
                        user_id=user_id
                    )
                    AccountingService.post_journal(journal_id, user_id)
                    logger.info(f"Created disposal entry {journal_id}")
                except ImportError:
                    logger.warning("Accounting module not available")
                
                AuditLogger.log(user_id, 'DISPOSE_ASSET', 'assets', asset_id,
                              new_value=f"Amount:{disposal_amt}, Gain/Loss:{gain_loss}")
                
                logger.info(f"Disposed asset {asset_id}")
                
        except Exception as e:
            logger.error(f"Failed to dispose asset: {e}")
            raise
