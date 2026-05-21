"""
Thorough Database Analysis
Search ALL database files for Arabic content and actual user data.
"""
import sqlite3
import os

# Find all .db files
db_files = [f for f in os.listdir('.') if f.endswith('.db')]
print(f"Found {len(db_files)} database files:")
for f in db_files:
    size = os.path.getsize(f) / 1024
    print(f"  - {f} ({size:.1f} KB)")

print("\n" + "=" * 70)
print("SEARCHING FOR ARABIC/USER DATA IN ALL DATABASES")
print("=" * 70)

for db_file in db_files:
    print(f"\n>>> Analyzing: {db_file}")
    print("-" * 50)
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Skip system tables
            if table == 'sqlite_sequence':
                continue
                
            try:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Get sample data
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    rows = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Check for Arabic characters in data
                    has_arabic = False
                    sample_values = []
                    
                    for row in rows:
                        for val in row:
                            if val and isinstance(val, str):
                                # Check for Arabic Unicode range
                                if any('\u0600' <= c <= '\u06FF' for c in str(val)):
                                    has_arabic = True
                                    sample_values.append(val)
                    
                    if has_arabic:
                        print(f"\n  *** FOUND ARABIC DATA: {table} ({count} rows) ***")
                        for val in sample_values[:5]:
                            print(f"      Sample: {val}")
                    else:
                        # Show tables with significant data
                        if count > 0 and table not in ['audit_logs', 'users', 'roles']:
                            # Get a name-like column
                            name_cols = [c for c in columns if 'name' in c.lower()]
                            if name_cols:
                                cursor.execute(f"SELECT {name_cols[0]} FROM {table} LIMIT 5")
                                names = [r[0] for r in cursor.fetchall() if r[0]]
                                if names:
                                    print(f"  {table}: {count} rows - {names[:3]}")
                            else:
                                print(f"  {table}: {count} rows")
                                
            except Exception as e:
                pass
                
        conn.close()
        
    except Exception as e:
        print(f"  Error: {e}")

# Also check Excel file
print("\n" + "=" * 70)
print("CHECKING EXCEL FILE")
print("=" * 70)

if os.path.exists('rale_data.xlsx'):
    try:
        import pandas as pd
        xl = pd.ExcelFile('rale_data.xlsx')
        print(f"\nExcel file: rale_data.xlsx")
        print(f"Sheets: {xl.sheet_names}")
        
        for sheet in xl.sheet_names[:3]:
            df = pd.read_excel(xl, sheet_name=sheet, nrows=5)
            print(f"\n  Sheet: {sheet}")
            print(f"  Columns: {list(df.columns)[:5]}...")
            
            # Check for Arabic
            for col in df.columns:
                for val in df[col].dropna():
                    if isinstance(val, str) and any('\u0600' <= c <= '\u06FF' for c in val):
                        print(f"    *** ARABIC FOUND in column '{col}': {val[:50]}")
                        break
    except Exception as e:
        print(f"  Error reading Excel: {e}")
