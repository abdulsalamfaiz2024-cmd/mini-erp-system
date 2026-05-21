"""
Shared Fixtures for Pytest
"""

import pytest
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Database

@pytest.fixture
def test_db():
    """Create a test database"""
    db_path = Path("test_erp_shared.db")
    
    # Remove if exists
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass # Use existing or fail later
    
    db = Database(db_path)
    yield db
    
    # Cleanup
    db.close()
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass
