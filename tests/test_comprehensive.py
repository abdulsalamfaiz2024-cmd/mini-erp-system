"""
Comprehensive Test Suite for Mini-ERP System
Tests core infrastructure, business logic, and performance
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import Database, get_db
from core.cache import LRUCache, cached, invalidate_cache, get_cache_stats
from core.performance import PerformanceMonitor, QueryTimer
from modules.sales.sales_manager import SalesManager
from modules.inventory.inventory_manager import InventoryManager
from modules.finance.finance_manager import FinanceManager


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_db():
    """Create a test database"""
    db_path = Path("test_erp.db")
    
    # Remove if exists
    if db_path.exists():
        db_path.unlink()
    
    db = Database(db_path)
    yield db
    
    # Cleanup
    db.close()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def sample_data(test_db):
    """Insert sample data for testing"""
    # Create test user
    test_db.insert('users', {
        'username': 'testuser',
        'password_hash': 'hash123',
        'full_name': 'Test User',
        'role_id': 1
    })
    
    # Create test customer
    test_db.insert('customers', {
        'customer_id': 'CUST001',
        'name': 'Test Customer',
        'email': 'test@example.com',
        'phone': '1234567890',
        'credit_limit': 10000,
        'current_balance': 0
    })
    
    # Create test products
    for i in range(5):
        test_db.insert('products', {
            'product_id': f'PROD{i:03d}',
            'name': f'Test Product {i}',
            'cost_price': 50 + i * 10,
            'selling_price': 100 + i * 20,
            'reorder_level': 20,
            'min_stock_level': 5
        })
        
        # Add inventory
        test_db.insert('inventory', {
            'product_id': f'PROD{i:03d}',
            'quantity': 100,
            'cost_price': 50 + i * 10,
            'warehouse_id': 1
        })
    
    return test_db


# ============================================================================
# CACHE TESTS
# ============================================================================

class TestCache:
    """Test caching system"""
    
    def test_lru_cache_basic(self):
        """Test basic cache operations"""
        cache = LRUCache(max_size=3, default_ttl=60)
        
        # Set and get
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
        
        # Non-existent key
        assert cache.get('nonexistent') is None
    
    def test_lru_cache_eviction(self):
        """Test LRU eviction"""
        cache = LRUCache(max_size=3, default_ttl=60)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        cache.set('key4', 'value4')  # Should evict key1
        
        assert cache.get('key1') is None
        assert cache.get('key4') == 'value4'
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = LRUCache(max_size=10, default_ttl=60)
        
        cache.set('key1', 'value1')
        cache.get('key1')  # Hit
        cache.get('key2')  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1
    
    def test_cache_decorator(self):
        """Test cache decorator"""
        cache = LRUCache(max_size=10, default_ttl=60)
        call_count = 0
        
        @cached(cache, 'test')
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)  # Should use cache
        
        assert result1 == result2 == 10
        assert call_count == 1  # Function called only once


# ============================================================================
# DATABASE TESTS
# ============================================================================

class TestDatabase:
    """Test database operations"""
    
    def test_bulk_insert(self, test_db):
        """Test bulk insert performance"""
        data_list = [
            {'customer_id': f'BULK{i:04d}', 'name': f'Customer {i}', 
             'email': f'customer{i}@test.com', 'phone': f'{i:010d}'}
            for i in range(100)
        ]
        
        ids = test_db.bulk_insert('customers', data_list)
        
        assert len(ids) == 100
        
        # Verify data
        count = test_db.fetch_one("SELECT COUNT(*) as cnt FROM customers WHERE customer_id LIKE 'BULK%'")
        assert count['cnt'] == 100
    
    def test_bulk_update(self, test_db, sample_data):
        """Test bulk update"""
        updates = [
            {
                'data': {'credit_limit': 20000},
                'where': ('customer_id = ?', ('CUST001',))
            }
        ]
        
        rows_updated = test_db.bulk_update('customers', updates)
        assert rows_updated == 1
        
        # Verify
        customer = test_db.fetch_one("SELECT credit_limit FROM customers WHERE customer_id = 'CUST001'")
        assert customer['credit_limit'] == 20000
    
    def test_transaction_rollback(self, test_db):
        """Test transaction rollback on error"""
        try:
            with test_db.transaction() as cursor:
                cursor.execute("INSERT INTO customers (customer_id, name) VALUES ('TX001', 'Test')")
                # Force error
                cursor.execute("INSERT INTO customers (customer_id, name) VALUES ('TX001', 'Duplicate')")
        except:
            pass
        
        # Verify rollback
        result = test_db.fetch_one("SELECT COUNT(*) as cnt FROM customers WHERE customer_id = 'TX001'")
        assert result['cnt'] == 0
    
    def test_query_stats(self, test_db, sample_data):
        """Test database statistics"""
        stats = test_db.get_query_stats()
        
        assert 'database_size_mb' in stats
        assert 'table_counts' in stats
        assert stats['table_counts']['products'] == 5


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance monitoring"""
    
    def test_query_timer(self):
        """Test query timing"""
        monitor = PerformanceMonitor()  # Create fresh instance
        
        # Record a query manually
        monitor.record_query('test_query', 0.05, 10)
        
        stats = monitor.get_query_stats()
        assert stats['total_queries'] > 0
        assert stats['total_queries'] == 1
    
    def test_slow_query_detection(self):
        """Test slow query detection"""
        monitor = PerformanceMonitor()
        
        # Record slow query
        monitor.record_query('SELECT * FROM large_table', 0.5, 1000)
        
        slow_queries = monitor.get_slow_queries(threshold=0.1)
        assert len(slow_queries) > 0
        assert slow_queries[0]['duration'] == 0.5


# ============================================================================
# BUSINESS LOGIC TESTS
# ============================================================================

class TestSalesFlow:
    """Test complete sales workflow"""
    
    def test_create_order(self, test_db, sample_data):
        """Test order creation"""
        items = [
            {
                'product_id': 'PROD000',
                'quantity': 2,
                'unit_price': 100,
                'tax_rate': 10,
                'discount_amount': 10
            }
        ]
        
        order_number = SalesManager.create_order('CUST001', items, 1, status='draft')
        
        assert order_number is not None
        assert order_number.startswith('SO-')
        
        # Verify order
        order = test_db.fetch_one("SELECT * FROM sales_orders WHERE order_number = ?", (order_number,))
        assert order is not None
        assert order['customer_id'] == 'CUST001'
        assert order['status'] == 'draft'
    
    def test_invoice_generation(self, test_db, sample_data):
        """Test invoice generation and stock deduction"""
        # Create order
        items = [
            {
                'product_id': 'PROD000',
                'quantity': 5,
                'unit_price': 100,
                'tax_rate': 0,
                'discount_amount': 0
            }
        ]
        
        order_number = SalesManager.create_order('CUST001', items, 1, status='draft')
        
        # Get initial stock
        initial_stock = InventoryManager.get_stock_level('PROD000')
        
        # Generate invoice
        SalesManager.generate_invoice(order_number, 1)
        
        # Verify stock deduction
        final_stock = InventoryManager.get_stock_level('PROD000')
        assert final_stock == initial_stock - 5
        
        # Verify order status
        order = test_db.fetch_one("SELECT status FROM sales_orders WHERE order_number = ?", (order_number,))
        assert order['status'] == 'invoiced'


class TestInventoryManagement:
    """Test inventory operations"""
    
    def test_fifo_deduction(self, test_db, sample_data):
        """Test FIFO stock deduction"""
        # Add multiple batches
        InventoryManager.add_stock('PROD000', 10, 50, warehouse_id=1, user_id=1)
        InventoryManager.add_stock('PROD000', 10, 60, warehouse_id=1, user_id=1)
        
        # Deduct stock
        consumed = InventoryManager.deduct_stock('PROD000', 15, user_id=1)
        
        # Should consume from oldest batch first
        assert len(consumed) == 2
        assert consumed[0]['quantity'] == 10  # First batch fully consumed
        assert consumed[1]['quantity'] == 5   # Second batch partially consumed
    
    def test_stock_availability_check(self, test_db, sample_data):
        """Test stock availability check"""
        available = InventoryManager.check_stock_availability('PROD000', 50)
        assert available is True
        
        available = InventoryManager.check_stock_availability('PROD000', 200)
        assert available is False


class TestFinancialCalculations:
    """Test financial calculations"""
    
    def test_profit_loss_calculation(self, test_db, sample_data):
        """Test P&L calculation"""
        # Create some sales
        items = [
            {
                'product_id': 'PROD000',
                'quantity': 2,
                'unit_price': 100,
                'tax_rate': 0,
                'discount_amount': 0
            }
        ]
        
        order_number = SalesManager.create_order('CUST001', items, 1)
        SalesManager.generate_invoice(order_number, 1)
        
        # Calculate P&L
        today = datetime.now().date()
        pl = FinanceManager.get_profit_loss(today.isoformat(), today.isoformat())
        
        assert pl['revenue'] > 0
        assert pl['cogs'] > 0
        assert pl['gross_profit'] > 0


# ============================================================================
# PERFORMANCE BENCHMARKS
# ============================================================================

@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmarks"""
    
    def test_bulk_insert_performance(self, test_db, benchmark):
        """Benchmark bulk insert"""
        data_list = [
            {'customer_id': f'PERF{i:06d}', 'name': f'Customer {i}'}
            for i in range(1000)
        ]
        
        result = benchmark(test_db.bulk_insert, 'customers', data_list)
        assert len(result) == 1000
    
    def test_fifo_calculation_performance(self, test_db, sample_data, benchmark):
        """Benchmark FIFO calculation"""
        # Add many batches
        for i in range(100):
            InventoryManager.add_stock('PROD000', 10, 50 + i, user_id=1)
        
        result = benchmark(InventoryManager.deduct_stock, 'PROD000', 500, user_id=1)
        assert len(result) > 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
