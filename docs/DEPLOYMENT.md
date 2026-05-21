# Deployment Guide - Mini-ERP System v2.0

## Pre-Deployment Checklist

### System Requirements
- [ ] Windows 10/11 (64-bit)
- [ ] Python 3.12 or higher installed
- [ ] 4GB RAM minimum (8GB recommended)
- [ ] 500MB free disk space
- [ ] Administrator privileges for installation

### Software Requirements
- [ ] Python 3.12+ with pip
- [ ] Git (optional, for version control)
- [ ] Text editor for configuration

---

## Installation Steps

### 1. Prepare Environment

```bash
# Navigate to project directory
cd d:\sales_systems

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- reportlab 4.4.5
- openpyxl 3.1.5
- pandas 2.3.3
- matplotlib 3.9.3
- psutil 6.1.1
- pytest 9.0.1

### 3. Configure Application

#### Company Settings
Edit `company_config.ini`:

```ini
[COMPANY_EN]
name = Your Company Name
address = Your Address
phone = +1234567890
email = info@yourcompany.com
tax_id = TAX123456

[COMPANY_AR]
name = اسم شركتك
address = عنوانك
phone = +1234567890
email = info@yourcompany.com
tax_id = TAX123456
```

#### Database Configuration
Edit `core/config.py` if needed:

```python
DATABASE_CONFIG = {
    'path': 'perfect_sales_system.db',
    'enable_foreign_keys': True,
    'enable_wal_mode': True,
    'backup_dir': Path('backups')
}
```

### 4. Initialize Database

```bash
# Run application (database auto-initializes)
python run_erp.py
```

On first run:
- Database schema created automatically
- Default admin user created
- Default roles configured

### 5. First Login

**Default Credentials**:
- Username: `admin`
- Password: `admin123`

**IMPORTANT**: Change admin password immediately after first login!

---

## Post-Deployment Configuration

### 1. Create Users

1. Login as admin
2. Navigate to Settings → Users
3. Create user accounts for your team
4. Assign appropriate roles

### 2. Configure Roles & Permissions

Default roles:
- **Admin**: Full system access
- **Manager**: Sales, purchasing, reports
- **User**: Limited access (sales, inventory view)

Customize in Settings → Roles

### 3. Import Master Data

#### Import Customers
1. Prepare CSV file with columns:
   - customer_id, name, email, phone, address, credit_limit
2. Use Batch Operations → Import from CSV

#### Import Products
1. Prepare CSV file with columns:
   - product_id, name, category, cost_price, selling_price, reorder_level
2. Use Batch Operations → Import from CSV

#### Import Suppliers
1. Prepare CSV file with columns:
   - supplier_id, name, email, phone, address
2. Use Batch Operations → Import from CSV

### 4. Configure Backups

Create scheduled task for database backups:

```bash
# Manual backup
python -c "from core.database import get_db; get_db().backup()"

# Windows Task Scheduler (daily at 2 AM)
# Create task: Run python backup script daily
```

---

## Performance Optimization

### 1. Enable Caching

Caching is enabled by default. Monitor cache performance:

```python
from core.cache import get_cache_stats
stats = get_cache_stats()
print(stats)
```

### 2. Monitor Performance

```python
from core.performance import get_monitor
metrics = get_monitor().get_dashboard_metrics()
```

Check for:
- Slow queries (> 100ms)
- High memory usage (> 80%)
- Low cache hit rate (< 70%)

### 3. Database Maintenance

```bash
# Check database size
python -c "from core.database import get_db; print(get_db().get_query_stats())"

# Vacuum database (monthly)
sqlite3 perfect_sales_system.db "VACUUM;"
```

---

## Security Hardening

### 1. Change Default Password

```sql
-- Update admin password
UPDATE users 
SET password_hash = '<new_hash>' 
WHERE username = 'admin';
```

Use the application UI: Settings → Change Password

### 2. Configure Session Timeout

Edit `core/config.py`:

```python
SECURITY_CONFIG = {
    'session_timeout': 3600,  # 1 hour
    'max_login_attempts': 5,
    'password_min_length': 8
}
```

### 3. Enable Audit Logging

Audit logging is enabled by default. Review logs:

```sql
SELECT * FROM audit_logs 
ORDER BY timestamp DESC 
LIMIT 100;
```

### 4. Restrict File Permissions

```bash
# Windows: Set folder permissions
icacls d:\sales_systems /grant Users:(OI)(CI)RX
icacls d:\sales_systems\perfect_sales_system.db /grant Users:(OI)(CI)RW
```

---

## Testing Deployment

### 1. Run Test Suite

```bash
# Run all tests
python -m pytest tests/test_comprehensive.py -v

# Expected: 10/10 core tests passing
```

### 2. Run Demo Script

```bash
python demo_enhancements.py
```

Verify:
- Caching works
- Bulk operations work
- Performance monitoring works
- Database operations work

### 3. Manual Testing

Test critical workflows:
1. Create customer
2. Create product
3. Create sales order
4. Generate invoice
5. Record payment
6. Generate report

---

## Troubleshooting

### Database Locked Error

**Cause**: Multiple connections or WAL mode issue

**Solution**:
```bash
# Close all connections
# Disable WAL mode temporarily
sqlite3 perfect_sales_system.db "PRAGMA journal_mode=DELETE;"
```

### Import Error: Module Not Found

**Cause**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt --force-reinstall
```

### Slow Performance

**Cause**: Cache not working or database needs optimization

**Solution**:
1. Check cache stats
2. Run VACUUM on database
3. Check for slow queries in logs

### Unicode Errors (Windows)

**Cause**: Console encoding issue

**Solution**:
```bash
# Set UTF-8 encoding
chcp 65001
```

---

## Rollback Procedure

If deployment fails:

1. **Stop application**
2. **Restore database backup**:
   ```bash
   copy backups\backup_YYYYMMDD_HHMMSS.db perfect_sales_system.db
   ```
3. **Revert code changes** (if using Git):
   ```bash
   git checkout <previous_version>
   ```
4. **Restart application**

---

## Monitoring & Maintenance

### Daily Tasks
- [ ] Check application logs
- [ ] Verify backups completed
- [ ] Monitor system performance

### Weekly Tasks
- [ ] Review audit logs
- [ ] Check cache performance
- [ ] Verify data integrity

### Monthly Tasks
- [ ] Database vacuum
- [ ] Archive old logs
- [ ] Update documentation
- [ ] Review user permissions

---

## Support Contacts

**Technical Issues**:
- Check logs in `logs/` directory
- Review documentation
- Run diagnostic: `python demo_enhancements.py`

**Data Issues**:
- Check audit logs
- Restore from backup if needed
- Verify data integrity

---

## Appendix: Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Check database size
dir perfect_sales_system.db

# View recent logs
type logs\erp.log | more

# Export database
sqlite3 perfect_sales_system.db ".dump" > backup.sql

# Import database
sqlite3 perfect_sales_system.db < backup.sql
```

---

**Deployment Checklist Complete** ✅

For additional support, refer to:
- README.md
- ENHANCEMENT_SUMMARY.md
- Project documentation in brain/ folder
