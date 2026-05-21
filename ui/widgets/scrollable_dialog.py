"""
Scrollable Dialog Base Class
Provides scrollable modal dialogs that work on small screens
"""

import tkinter as tk
from tkinter import ttk


class ScrollableDialog(tk.Toplevel):
    """
    Base class for modal dialogs with scrollable content.
    Automatically handles max height and vertical scrolling.
    """
    
    def __init__(self, parent, title="Dialog", width=600, max_height=700):
        """
        Initialize scrollable dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width in pixels
            max_height: Maximum height before scrolling activates
        """
        super().__init__(parent)
        
        self.title(title)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.parent = parent
        self.dialog_width = width
        self.dialog_max_height = max_height
        
        # Main container with fixed width
        self.main_frame = ttk.Frame(self, width=width)
        self.main_frame.pack(fill='both', expand=True)
        self.main_frame.pack_propagate(False)
        
        # Create canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.canvas.yview)
        
        # Scrollable frame inside canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Content frame (subclasses use this)
        self.content = ttk.Frame(self.scrollable_frame, padding=20)
        self.content.pack(fill='both', expand=True)
        
        # Update size after creation
        self.after(100, self._adjust_size)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _adjust_size(self):
        """Adjust dialog size based on content"""
        self.update_idletasks()
        
        # Get actual content height
        content_height = self.scrollable_frame.winfo_reqheight()
        
        # Determine dialog height (capped at max_height)
        dialog_height = min(content_height + 40, self.dialog_max_height)
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Further cap at 90% of screen height
        dialog_height = min(dialog_height, int(screen_height * 0.9))
        
        # Center position
        x = (screen_width - self.dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        # Set geometry
        self.geometry(f"{self.dialog_width}x{dialog_height}+{x}+{y}")
        
        # Show scrollbar only if needed
        if content_height > dialog_height:
            self.scrollbar.pack(side='right', fill='y')
        else:
            self.scrollbar.pack_forget()
    
    def add_ok_cancel_buttons(self, ok_command, cancel_command=None):
        """
        Add standard OK/Cancel buttons at bottom
        
        Args:
            ok_command: Command for OK button
            cancel_command: Command for Cancel (defaults to destroy)
        """
        if cancel_command is None:
            cancel_command = self.destroy
        
        button_frame = ttk.Frame(self.content)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=cancel_command
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="OK",
            command=ok_command,
            style='Success.TButton'
        ).pack(side='right', padx=5)
    
    def destroy(self):
        """Clean up mouse wheel binding"""
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()
