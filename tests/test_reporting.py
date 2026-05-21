"""
Test script for Reporting logic
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))

from modules.reporting.reporting_manager import ReportingManager
from core.database import get_db

def test_reporting():
    print("Testing Reporting Module...")
    
    # 1. Sales Report
    print("\n1. Sales Report...")
    today = datetime.now().strftime('%Y-%m-%d')
    data = ReportingManager.get_sales_report(today, today)
    print(f"Sales Rows: {len(data)}")
    if len(data) > 0:
        print(f"[OK] Sales Data Found: {data[0]['order_number']}")
    else:
        print("[INFO] No sales for today found (Expected depending on previous tests)")

    # 2. Inventory Report
    print("\n2. Inventory Report...")
    data = ReportingManager.get_inventory_report()
    print(f"Inventory Items: {len(data)}")
    if len(data) > 0:
         print(f"[OK] Inventory Data Found: {data[0]['name']}")
         
    # 3. Test Exports
    print("\n3. Testing Exports...")
    try:
        sales_data = ReportingManager.get_sales_report(today, today)
        if sales_data:
            # Test CSV
            csv_path = "test_sales_report.csv"
            ReportingManager.export_to_csv(sales_data, csv_path)
            if Path(csv_path).exists() and Path(csv_path).stat().st_size > 0:
                print(f"[OK] CSV Export Success ({csv_path})")
            
            # Test PDF
            pdf_path = "test_sales_report.pdf"
            ReportingManager.export_sales_report_pdf(sales_data, pdf_path)
            if Path(pdf_path).exists() and Path(pdf_path).stat().st_size > 0:
                print(f"[OK] PDF Export Success ({pdf_path})")
            
            # Test Excel
            xlsx_path = "test_sales_report.xlsx"
            ReportingManager.export_to_excel(sales_data, xlsx_path)
            if Path(xlsx_path).exists() and Path(xlsx_path).stat().st_size > 0:
                print(f"[OK] Excel Export Success ({xlsx_path})")
                
        else:
            print("[INFO] Skipping export tests (no data)")
            
    except Exception as e:
        print(f"[FAIL] Export test failed: {e}")
        import traceback
        traceback.print_exc()
    
if __name__ == "__main__":
    test_reporting()
