"""
Database Migration Runner
Runs all pending migrations in order
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_db
import importlib.util


def get_migration_files():
    """Get all migration files in order"""
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and f[0].isdigit()]
    return sorted(files)


def run_migration(filepath):
    """Run a single migration file"""
    # Load migration module
    spec = importlib.util.spec_from_file_location("migration", filepath)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    # Run the up() function
    migration.up()


def main():
    """Run all migrations"""
    print("=" * 70)
    print("DATABASE MIGRATION RUNNER")
    print("=" * 70)
    
    migrations_dir = os.path.dirname(os.path.abspath(__file__))
    migration_files = get_migration_files()
    
    if not migration_files:
        print("\n[INFO] No migrations found")
        return
    
    print(f"\n[INFO] Found {len(migration_files)} migration(s):\n")
    for f in migration_files:
        print(f"  - {f}")
    
    print("\n" + "=" * 70)
    print("RUNNING MIGRATIONS")
    print("=" * 70 + "\n")
    
    for migration_file in migration_files:
        filepath = os.path.join(migrations_dir, migration_file)
        print(f"\n>>> Running {migration_file}...")
        print("-" * 70)
        
        try:
            run_migration(filepath)
            print(f"[OK] {migration_file} completed\n")
        except Exception as e:
            print(f"[ERROR] {migration_file} failed: {e}")
            import traceback
            traceback.print_exc()
            print("\n[ABORT] Migration process stopped due to error")
            return 1
    
    print("\n" + "=" * 70)
    print("ALL MIGRATIONS COMPLETED SUCCESSFULLY")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code or 0)
