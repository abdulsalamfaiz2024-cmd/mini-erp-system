import pandas as pd
import os
import sys

# Force utf-8 for file output
sys.stdout.reconfigure(encoding='utf-8')

FILE_PATH = "rale_data.xlsx"
OUTPUT_FILE = "excel_schema.txt"

def inspect_excel():
    if not os.path.exists(FILE_PATH):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"File not found: {FILE_PATH}")
        return

    try:
        xl = pd.ExcelFile(FILE_PATH)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"Sheets found: {xl.sheet_names}\n\n")
            
            for sheet in xl.sheet_names:
                f.write(f"--- Sheet: {sheet} ---\n")
                # Read header only
                df = xl.parse(sheet, nrows=0) 
                columns = list(df.columns)
                f.write(f"Columns ({len(columns)}): {columns}\n")
                
                # Sample 3 rows for data type checking (careful with read)
                try:
                    df_sample = xl.parse(sheet, nrows=3)
                    f.write("Sample Data (First 3 rows):\n")
                    # Convert to string to avoid encoding crash during write if pandas fails
                    f.write(df_sample.to_string()) 
                    f.write("\n\n")
                except Exception as e:
                    f.write(f"Could not read sample data: {e}\n\n")

        print(f"Schema written to {OUTPUT_FILE}")
            
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    inspect_excel()
