"""
Base Page Component
All pages inherit from this to enforce consistent structure
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import Theme
from ui.layout.topbar import TopBar
from abc import ABC, abstractmethod


class BasePage(ttk.Frame, ABC):
    """
    Base class for all ERP pages.
    
    Enforces:
    - Top action bar
    - Scrollable content area
    - API binding documentation
    - Consistent error handling
    """
    
    def __init__(self, parent, user_data, page_title="Page"):
        super().__init__(parent, style='Main.TFrame')
        self.user_data = user_data
        self.page_title = page_title
        
        # Setup structure
        self.topbar = TopBar(self)
        self.topbar.pack(fill='x', side='top')
        self.topbar.set_page_title(page_title)
        
        # Scrollable content area
        self.content_canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        self.content_scrollbar = ttk.Scrollbar(
            self, 
            orient='vertical', 
            command=self.content_canvas.yview
        )
        self.content_scrollbar.pack(side='right', fill='y')
        self.content_canvas.pack(side='left', fill='both', expand=True)
        
        # Content frame inside canvas
        self.content_frame = tk.Frame(self.content_canvas, bg='white')
        self.canvas_window = self.content_canvas.create_window(
            (0, 0), 
            window=self.content_frame, 
            anchor='nw'
        )
        
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        
        # Bind mousewheel globally when canvas is focused or hovered
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Bind resize
        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.content_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # TEMPORARY: Log initialization
        print(f"INIT OK: {page_title}")
        
        # Call subclass setup
        print(f"  -> setup_actions()")
        self.setup_actions()
        
        print(f"  -> setup_content()")
        self.setup_content()
        
        print(f"LOAD_DATA START: {page_title}")
        try:
            self.load_data()
            print(f"LOAD_DATA END: {page_title}")
        except Exception as e:
            print(f"ERROR LOAD_DATA FAILED: {page_title} - {e}")
            # Re-raise to maintain error visibility
            raise


    def _on_mousewheel(self, event):
        """Handle global mousewheel scrolling"""
        # Only scroll if the mouse is over the content area
        try:
            x, y = self.winfo_pointerxy()
            widget_under_mouse = self.winfo_containing(x, y)
            
            # Check if widget is part of this page content
            if widget_under_mouse and str(self) in str(widget_under_mouse):
                # Scroll only if vertical scrollbar is active
                if self.content_scrollbar.get() != (0.0, 1.0):
                    self.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception:
            pass
    
    def _on_frame_configure(self, event=None):
        """Reset scroll region when content changes"""
        self.content_canvas.configure(scrollregion=self.content_canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        """Resize content frame to canvas width"""
        canvas_width = event.width
        self.content_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    @abstractmethod
    def setup_actions(self):
        """
        Override this to populate topbar actions.
        
        Example:
            self.topbar.set_actions([
                {'text': 'New Order', 'command': self.new_order, 'icon': '➕'},
                {'text': 'Submit', 'command': self.submit},
            ])
        """
        pass
    
    @abstractmethod
    def setup_content(self):
        """
        Override this to build page content.
        Add all widgets to self.content_frame.
        
        Example:
            ttk.Label(self.content_frame, text="Hello").pack()
        """
        pass
    
    @abstractmethod
    def load_data(self):
        """
        Override this to load page data.
        Called after UI setup.
        """
        pass
    
    def call_api(self, api_name, api_func, *args, success_msg=None, **kwargs):
        """
        Standardized API calling wrapper with error handling.
        
        Args:
            api_name: Name of API for logging (e.g. 'SalesOrderService.create_order')
            api_func: The actual API function to call
            success_msg: Optional success message to show
            *args, **kwargs: Passed to api_func
        
        Returns:
            API result or None on error
        """
        try:
            result = api_func(*args, **kwargs)
            
            if success_msg:
                messagebox.showinfo("Success", success_msg)
            
            # Log API call (could integrate with audit)
            print(f"[API Call] {api_name} - Success")
            
            return result
            
        except Exception as e:
            error_msg = f"{api_name} failed: {str(e)}"
            messagebox.showerror("API Error", error_msg)
            print(f"[API Call] {api_name} - Error: {e}")
            return None
    
    def refresh(self):
        """Refresh page data"""
        self.load_data()
    
    def get_employee_id(self):
        """Get current user's employee ID"""
        from core.database import get_db
        db = get_db()
        row = db.fetch_one(
            "SELECT employee_id FROM employees WHERE user_id=?", 
            (self.user_data['id'],)
        )
        return row['employee_id'] if row else None
