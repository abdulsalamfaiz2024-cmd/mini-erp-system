"""
Master Workflow Setup Script
Registers all 7 workflows into the database
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.sales.setup_workflow import setup_sales_workflow
from scripts.setup_return_workflow import setup_sales_return_workflow
from scripts.setup_count_workflow import setup_inventory_count_workflow
from scripts.setup_issue_workflow import setup_issue_order_workflow
from scripts.setup_expense_workflow import setup_expense_workflow
from scripts.setup_journal_workflow import setup_journal_workflow
from scripts.setup_asset_workflow import setup_asset_workflow


def setup_all_workflows():
    """
    Register all 7 ERP workflows
    
    Idempotent: Can be run multiple times safely
    """
    print("=" * 70)
    print("  WORKFLOW DATABASE REGISTRATION")
    print("  Registering all ERP workflows")
    print("=" * 70)
    print()
    
    workflows = []
    errors = []
    
    # 1. Sales Order (existing)
    try:
        wf_id = setup_sales_workflow()
        workflows.append(("SALES_ORDER", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("SALES_ORDER", str(e)))
        workflows.append(("SALES_ORDER", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # 2. Sales Return
    try:
        wf_id = setup_sales_return_workflow()
        workflows.append(("SALES_RETURN", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("SALES_RETURN", str(e)))
        workflows.append(("SALES_RETURN", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # 3. Inventory Count
    try:
        wf_id = setup_inventory_count_workflow()
        workflows.append(("INVENTORY_COUNT", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("INVENTORY_COUNT", str(e)))
        workflows.append(("INVENTORY_COUNT", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # 4. Issue Order
    try:
        wf_id = setup_issue_order_workflow()
        workflows.append(("ISSUE_ORDER", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("ISSUE_ORDER", str(e)))
        workflows.append(("ISSUE_ORDER", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # 5. Expense
    try:
        wf_id = setup_expense_workflow()
        workflows.append(("EXPENSE", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("EXPENSE", str(e)))
        workflows.append(("EXPENSE", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # 6. Journal Entry
    try:
        wf_id = setup_journal_workflow()
        workflows.append(("JOURNAL_ENTRY", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("JOURNAL_ENTRY", str(e)))
        workflows.append(("JOURNAL_ENTRY", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # 7. Asset
    try:
        wf_id = setup_asset_workflow()
        workflows.append(("ASSET", wf_id, "[OK]"))
    except Exception as e:
        errors.append(("ASSET", str(e)))
        workflows.append(("ASSET", None, "[ERROR]"))
        print(f"[ERROR] Error: {e}")
    
    # Summary
    print()
    print("=" * 70)
    print("  REGISTRATION SUMMARY")
    print("=" * 70)
    print()
    
    for doc_type, wf_id, status in workflows:
        print(f"{status} {doc_type:20s} {wf_id or 'FAILED':40s}")
    
    print()
    print(f"Total Workflows: {len(workflows)}")
    print(f"Success: {sum(1 for _, _, s in workflows if s == '[OK]')}")
    print(f"Failed: {len(errors)}")
    
    if errors:
        print()
        print("ERRORS:")
        for doc_type, error in errors:
            print(f"  {doc_type}: {error}")
        return False
    else:
        print()
        print("[OK] ALL WORKFLOWS REGISTERED SUCCESSFULLY")
        return True


if __name__ == "__main__":
    success = setup_all_workflows()
    sys.exit(0 if success else 1)
