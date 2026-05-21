"""
Batch Operations Module
Provides bulk actions for data management
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Callable
import csv
from datetime import datetime

from core.database import get_db
from core.logger import get_logger
from core.cache import invalidate_cache
from ui.styles import Theme

logger = get_logger('batch_operations')


class BatchOperationsManager:
    """Manages batch operations on entities"""
    
    @staticmethod
    def bulk_update_status(entity_type: str, entity_ids: List[str], new_status: str, user_id: int) -> int:
        """
        Update status for multiple entities
        
        Args:
            entity_type: Type of entity (customers, products, orders)
            entity_ids: List of entity IDs
            new_status: New status value
            user_id: User performing the operation
            
        Returns:
            Number of records updated
        """
        if not entity_ids:
            return 0
        
        try:
            db = get_db()
            
            # Map entity types to tables
            table_map = {
                'customers': 'customers',
                'products': 'products',
                'orders': 'sales_orders',
                'suppliers': 'suppliers'
            }
            
            table = table_map.get(entity_type)
            if not table:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            # Build bulk update
            updates = [
                {
                    'data': {'status': new_status, 'updated_by': user_id},
                    'where': (f'{entity_type[:-1]}_id = ?' if entity_type != 'orders' else 'order_number = ?', (eid,))
                }
                for eid in entity_ids
            ]
            
            count = db.bulk_update(table, updates)
            
            # Invalidate cache
            invalidate_cache(entity_type[:-1])
            
            logger.info(f"Bulk updated {count} {entity_type} to status '{new_status}'")
            return count
            
        except Exception as e:
            logger.error(f"Bulk update failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def bulk_delete(entity_type: str, entity_ids: List[str], user_id: int, soft: bool = True) -> int:
        """
        Delete multiple entities
        
        Args:
            entity_type: Type of entity
            entity_ids: List of entity IDs
            user_id: User performing the operation
            soft: If True, soft delete (set deleted_at), else hard delete
            
        Returns:
            Number of records deleted
        """
        if not entity_ids:
            return 0
        
        try:
            db = get_db()
            
            table_map = {
                'customers': 'customers',
                'products': 'products',
                'orders': 'sales_orders',
                'suppliers': 'suppliers'
            }
            
            table = table_map.get(entity_type)
            if not table:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            if soft:
                # Soft delete
                updates = [
                    {
                        'data': {'deleted_at': datetime.now().isoformat(), 'updated_by': user_id},
                        'where': (f'{entity_type[:-1]}_id = ?' if entity_type != 'orders' else 'order_number = ?', (eid,))
                    }
                    for eid in entity_ids
                ]
                count = db.bulk_update(table, updates)
            else:
                # Hard delete
                id_field = f'{entity_type[:-1]}_id' if entity_type != 'orders' else 'order_number'
                placeholders = ','.join(['?' for _ in entity_ids])
                count = db.execute(
                    f"DELETE FROM {table} WHERE {id_field} IN ({placeholders})",
                    tuple(entity_ids)
                ).rowcount
            
            # Invalidate cache
            invalidate_cache(entity_type[:-1])
            
            logger.info(f"Bulk deleted {count} {entity_type}")
            return count
            
        except Exception as e:
            logger.error(f"Bulk delete failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def export_to_csv(entity_type: str, entity_ids: List[str], filepath: str) -> bool:
        """
        Export entities to CSV
        
        Args:
            entity_type: Type of entity
            entity_ids: List of entity IDs (empty for all)
            filepath: Output CSV file path
            
        Returns:
            True if successful
        """
        try:
            db = get_db()
            
            # Build query
            table_map = {
                'customers': ('customers', 'customer_id'),
                'products': ('products', 'product_id'),
                'orders': ('sales_orders', 'order_number'),
                'suppliers': ('suppliers', 'supplier_id')
            }
            
            table, id_field = table_map.get(entity_type, (None, None))
            if not table:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            # Fetch data
            if entity_ids:
                placeholders = ','.join(['?' for _ in entity_ids])
                query = f"SELECT * FROM {table} WHERE {id_field} IN ({placeholders})"
                rows = db.fetch_all(query, tuple(entity_ids))
            else:
                query = f"SELECT * FROM {table} WHERE deleted_at IS NULL"
                rows = db.fetch_all(query)
            
            if not rows:
                logger.warning("No data to export")
                return False
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows([dict(row) for row in rows])
            
            logger.info(f"Exported {len(rows)} {entity_type} to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}", exc_info=True)
            raise
    
    @staticmethod
    def import_from_csv(entity_type: str, filepath: str, user_id: int, 
                       update_existing: bool = False) -> Dict[str, int]:
        """
        Import entities from CSV
        
        Args:
            entity_type: Type of entity
            filepath: Input CSV file path
            user_id: User performing the import
            update_existing: If True, update existing records
            
        Returns:
            Dict with counts: {'inserted': N, 'updated': N, 'errors': N}
        """
        try:
            db = get_db()
            
            table_map = {
                'customers': ('customers', 'customer_id'),
                'products': ('products', 'product_id'),
                'suppliers': ('suppliers', 'supplier_id')
            }
            
            table, id_field = table_map.get(entity_type, (None, None))
            if not table:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            # Read CSV
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                return {'inserted': 0, 'updated': 0, 'errors': 0}
            
            inserted = 0
            updated = 0
            errors = 0
            
            for row in rows:
                try:
                    # Add metadata
                    row['created_by'] = user_id
                    row['updated_by'] = user_id
                    
                    # Check if exists
                    entity_id = row.get(id_field)
                    if entity_id:
                        existing = db.fetch_one(
                            f"SELECT id FROM {table} WHERE {id_field} = ?",
                            (entity_id,)
                        )
                        
                        if existing and update_existing:
                            # Update
                            db.update(table, row, f'{id_field} = ?', (entity_id,))
                            updated += 1
                        elif not existing:
                            # Insert
                            db.insert(table, row)
                            inserted += 1
                    else:
                        # Insert without ID (will auto-generate)
                        db.insert(table, row)
                        inserted += 1
                        
                except Exception as e:
                    logger.error(f"Failed to import row: {e}")
                    errors += 1
            
            # Invalidate cache
            invalidate_cache(entity_type[:-1])
            
            logger.info(f"Import complete: {inserted} inserted, {updated} updated, {errors} errors")
            return {'inserted': inserted, 'updated': updated, 'errors': errors}
            
        except Exception as e:
            logger.error(f"Import failed: {e}", exc_info=True)
            raise


class BatchOperationsDialog(tk.Toplevel):
    """Dialog for batch operations on selected items"""
    
    def __init__(self, parent, entity_type: str, selected_ids: List[str], 
                 on_complete: Callable = None):
        super().__init__(parent)
        
        self.entity_type = entity_type
        self.selected_ids = selected_ids
        self.on_complete = on_complete
        
        self.setup_window()
        self.setup_ui()
    
    def setup_window(self):
        """Configure window"""
        self.title(f"Batch Operations - {len(self.selected_ids)} items selected")
        self.geometry("500x400")
        
        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (250)
        y = (self.winfo_screenheight() // 2) - (200)
        self.geometry(f"500x400+{x}+{y}")
        
        # Modal
        self.transient(self.master)
        self.grab_set()
        
        Theme.apply_styles(self)
    
    def setup_ui(self):
        """Setup UI"""
        container = ttk.Frame(self, style='Main.TFrame', padding=20)
        container.pack(fill='both', expand=True)
        
        # Header
        ttk.Label(
            container,
            text=f"Batch Operations",
            style='H1.TLabel',
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 5))
        
        ttk.Label(
            container,
            text=f"{len(self.selected_ids)} {self.entity_type} selected",
            style='Body.TLabel',
            foreground='#7f8c8d'
        ).pack(pady=(0, 20))
        
        # Operations
        ops_frame = ttk.LabelFrame(container, text="Available Operations", padding=15)
        ops_frame.pack(fill='both', expand=True, pady=10)
        
        # Update Status
        status_frame = ttk.Frame(ops_frame)
        status_frame.pack(fill='x', pady=5)
        
        ttk.Label(status_frame, text="Update Status:").pack(side='left', padx=(0, 10))
        
        self.status_var = tk.StringVar(value='active')
        status_combo = ttk.Combobox(
            status_frame,
            textvariable=self.status_var,
            values=['active', 'inactive', 'pending', 'archived'],
            state='readonly',
            width=15
        )
        status_combo.pack(side='left', padx=(0, 10))
        
        ttk.Button(
            status_frame,
            text="Apply",
            command=self.update_status,
            style='Primary.TButton'
        ).pack(side='left')
        
        # Separator
        ttk.Separator(ops_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Export
        export_frame = ttk.Frame(ops_frame)
        export_frame.pack(fill='x', pady=5)
        
        ttk.Label(export_frame, text="Export to CSV:").pack(side='left', padx=(0, 10))
        
        ttk.Button(
            export_frame,
            text="Export Selected",
            command=self.export_csv
        ).pack(side='left', padx=5)
        
        # Separator
        ttk.Separator(ops_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Delete
        delete_frame = ttk.Frame(ops_frame)
        delete_frame.pack(fill='x', pady=5)
        
        ttk.Label(delete_frame, text="Delete:").pack(side='left', padx=(0, 10))
        
        ttk.Button(
            delete_frame,
            text="Soft Delete",
            command=lambda: self.delete_items(soft=True)
        ).pack(side='left', padx=5)
        
        ttk.Button(
            delete_frame,
            text="Hard Delete",
            command=lambda: self.delete_items(soft=False),
            style='Danger.TButton'
        ).pack(side='left', padx=5)
        
        # Close button
        ttk.Button(
            container,
            text="Close",
            command=self.destroy
        ).pack(pady=20)
    
    def update_status(self):
        """Update status for selected items"""
        try:
            new_status = self.status_var.get()
            
            if not messagebox.askyesno(
                "Confirm",
                f"Update status to '{new_status}' for {len(self.selected_ids)} items?"
            ):
                return
            
            count = BatchOperationsManager.bulk_update_status(
                self.entity_type,
                self.selected_ids,
                new_status,
                user_id=1  # TODO: Get from session
            )
            
            messagebox.showinfo("Success", f"Updated {count} items")
            
            if self.on_complete:
                self.on_complete()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}")
    
    def export_csv(self):
        """Export selected items to CSV"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"{self.entity_type}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not filepath:
                return
            
            BatchOperationsManager.export_to_csv(
                self.entity_type,
                self.selected_ids,
                filepath
            )
            
            messagebox.showinfo("Success", f"Exported to {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def delete_items(self, soft: bool = True):
        """Delete selected items"""
        try:
            delete_type = "soft delete" if soft else "permanently delete"
            
            if not messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to {delete_type} {len(self.selected_ids)} items?\n\n"
                f"{'This can be undone.' if soft else 'This CANNOT be undone!'}"
            ):
                return
            
            count = BatchOperationsManager.bulk_delete(
                self.entity_type,
                self.selected_ids,
                user_id=1,  # TODO: Get from session
                soft=soft
            )
            
            messagebox.showinfo("Success", f"Deleted {count} items")
            
            if self.on_complete:
                self.on_complete()
            
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")
