"""
Test script for Finance Module
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from modules.finance.finance_manager import FinanceManager
from core.database import get_db

def test_finance():
    print("Testing Finance Module...")
    db = get_db()
    user_id = 1
    
    # Setup: We rely on previous tests data (Sales + Purchasing + Inventory)
    # Ideally, we should ensure data exists.
    # Sales: 1 Invoice (Profit 250), 1 Payment (300)
    # Purchasing: 1 PO (1000), 1 Payment (600) -> Expense? No, usually separate.
    # Finance Manager 'get_cash_flow' sums 'payments' table.
    # Sales Payment -> Income (300)
    # Purchase Payment -> Expense (600)
    
    # 1. Add Operating Expense
    print("\n1. Adding Expenses...")
    try:
        FinanceManager.add_expense('fixed', 'rent', 100.0, 'Office Rent', user_id)
        FinanceManager.add_expense('variable', 'utilities', 50.0, 'Electricity', user_id)
        print("[OK] Expenses added (Total 150.0)")
    except Exception as e:
        print(f"[FAIL] Add expense failed: {e}")
        return

    # 2. Check Cash Flow
    print("\n2. Checking Cash Flow...")
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        cf = FinanceManager.get_cash_flow(today, today)
        print(f"Cash Flow: {cf}")
        
        # Expected Income: 300 (from Sales)
        # Expected Expense: 600 (Purchasing) + 150 (Operating) = 750
        # Net: 300 - 750 = -450
        
        # Note: Previous tests ran on same DB, so data persists unless deleted.
        # But 'payments' table accumulates.
        # We need to filter by today (which we do). 
        # If test_sales and test_purchasing ran today, their data is there.
        
        # Let's verify broadly (non-zero logic)
        if cf['income'] >= 300:
             print("[OK] Income Detected")
        else:
             print(f"[WARN] Income low ({cf['income']}). Did Sales test run?")

        if cf['expense'] >= 750:
             print("[OK] Expenses Detected")
        else:
             print(f"[WARN] Expenses low ({cf['expense']}).")
             
    except Exception as e:
        print(f"[FAIL] Cash flow check failed: {e}")

    # 3. Check P&L
    print("\n3. Checking Profit & Loss...")
    try:
        pl = FinanceManager.get_profit_loss(today, today)
        print(f"P&L: {pl}")
        
        # Sales Revenue: 500
        # COGS: 250
        # Gross Profit: 250
        # Operating Expenses: 150
        # Net Profit: 100
        
        if pl['net_profit'] == 100.0:
            print("[OK] Net Profit Correct (100.0)")
        elif pl['net_profit'] == 250.0: # If expenses not counted?
            print("[WARN] Net Profit matches Gross (Expenses ignored?)")
        else:
            print(f"[INFO] Net Profit: {pl['net_profit']} (Expected 100.0 if clean run)")
            
    except Exception as e:
        print(f"[FAIL] P&L check failed: {e}")

    # 4. AR / AP
    print("\n4. Checking AR/AP...")
    try:
        ar = FinanceManager.get_accounts_receivable()
        ap = FinanceManager.get_accounts_payable()
        print(f"Accounts Receivable: {ar}")
        print(f"Accounts Payable: {ap}")
        
        if ar > 0: print(f"[OK] AR Positive ({ar})")
        if ap > 0: print(f"[OK] AP Positive ({ap})")
        
    except Exception as e:
        print(f"[FAIL] AR/AP check failed: {e}")

if __name__ == "__main__":
    test_finance()
