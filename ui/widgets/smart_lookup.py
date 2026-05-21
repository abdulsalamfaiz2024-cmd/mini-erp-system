"""
Smart Lookup Field Widget
ERP-style lookup field with autocomplete, dropdown, and bi-directional binding.

Features:
- Type-ahead autocomplete with debouncing
- Dropdown button showing all items in scrollable list
- Bi-directional binding (ID ↔ Name synchronization)
- Cached data for performance
- Keyboard navigation (↑↓ Enter Esc Tab)
- Visual feedback for validation states
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Tuple, Optional, Dict, Any
from functools import lru_cache


class SmartLookupField(ttk.Frame):
    """
    ERP-style lookup field with autocomplete and bi-directional binding.
    
    Args:
        parent: Parent widget
        label: Field label text
        data_source: Function(search_term) -> List of (id, name, extra_data) tuples
        id_var: StringVar for the ID field (optional, creates internal if None)
        name_var: StringVar for the Name field (optional, creates internal if None)
        on_select: Callback when item is selected: fn(id, name, extra_data)
        show_id_field: Whether to show a separate ID entry field
        placeholder: Placeholder text when empty
        required: Whether field is required (shows visual indicator)
    """
    
    # Debounce delay for autocomplete (ms)
    DEBOUNCE_MS = 300
    
    # Maximum items to show in dropdown
    MAX_DROPDOWN_ITEMS = 100
    
    # Maximum items to show in autocomplete
    MAX_AUTOCOMPLETE_ITEMS = 10
    
    def __init__(
        self,
        parent,
        label: str = "",
        data_source: Callable[[str], List[Tuple[str, str, Dict]]] = None,
        id_var: tk.StringVar = None,
        name_var: tk.StringVar = None,
        on_select: Callable[[str, str, Dict], None] = None,
        show_id_field: bool = False,
        placeholder: str = "Search or select...",
        required: bool = False,
        width: int = 300
    ):
        super().__init__(parent)
        
        self.label_text = label
        self.data_source = data_source or (lambda x: [])
        self.on_select_callback = on_select
        self.show_id_field = show_id_field
        self.placeholder = placeholder
        self.required = required
        self.field_width = width
        
        # Variables for binding
        self.id_var = id_var or tk.StringVar()
        self.name_var = name_var or tk.StringVar()
        
        # Internal state
        self._data_cache: List[Tuple[str, str, Dict]] = []
        self._debounce_id = None
        self._dropdown_window = None
        self._selected_index = -1
        self._is_syncing = False  # Prevent infinite loops
        self._last_valid_selection = None
        
        # Build UI
        self._setup_ui()
        self._setup_bindings()
        
    def _setup_ui(self):
        """Build the widget UI"""
        # Apply consistent styling
        self.configure(style='TFrame')
        
        # Label (if provided)
        if self.label_text:
            label_text = f"{self.label_text} *" if self.required else self.label_text
            self.label = ttk.Label(
                self,
                text=label_text,
                font=("Segoe UI", 10),
                foreground="#374151"
            )
            self.label.pack(anchor='w', pady=(0, 4))
        
        # Main input container
        self.input_frame = ttk.Frame(self)
        self.input_frame.pack(fill='x')
        
        # ID field (optional, shown separately)
        if self.show_id_field:
            id_frame = ttk.Frame(self.input_frame)
            id_frame.pack(side='left', padx=(0, 10))
            
            ttk.Label(id_frame, text="ID:", font=("Segoe UI", 9)).pack(anchor='w')
            self.id_entry = ttk.Entry(
                id_frame,
                textvariable=self.id_var,
                width=15,
                font=("Segoe UI", 10)
            )
            self.id_entry.pack(fill='x')
        
        # Name field with dropdown button
        name_container = ttk.Frame(self.input_frame)
        name_container.pack(side='left', fill='x', expand=True)
        
        # Entry container (for entry + button)
        entry_frame = tk.Frame(name_container, bg='white', bd=1, relief='solid')
        entry_frame.pack(fill='x')
        
        # Name entry
        self.name_entry = tk.Entry(
            entry_frame,
            textvariable=self.name_var,
            font=("Segoe UI", 10),
            bd=0,
            highlightthickness=0,
            bg='white'
        )
        self.name_entry.pack(side='left', fill='x', expand=True, padx=8, pady=6)
        
        # Dropdown button
        self.dropdown_btn = tk.Button(
            entry_frame,
            text="▼",
            font=("Segoe UI", 8),
            bd=0,
            bg='white',
            activebackground='#e5e7eb',
            cursor='hand2',
            width=3,
            command=self._toggle_dropdown
        )
        self.dropdown_btn.pack(side='right', padx=2, pady=2)
        
        # Placeholder handling
        self._show_placeholder()
        
    def _setup_bindings(self):
        """Setup event bindings"""
        # Name entry bindings
        self.name_entry.bind('<KeyRelease>', self._on_name_key)
        self.name_entry.bind('<FocusIn>', self._on_focus_in)
        self.name_entry.bind('<FocusOut>', self._on_focus_out)
        self.name_entry.bind('<Down>', self._on_arrow_down)
        self.name_entry.bind('<Up>', self._on_arrow_up)
        self.name_entry.bind('<Return>', self._on_enter)
        self.name_entry.bind('<Escape>', self._on_escape)
        self.name_entry.bind('<Tab>', self._on_tab)
        
        # ID entry bindings (if shown)
        if self.show_id_field:
            self.id_entry.bind('<KeyRelease>', self._on_id_key)
            self.id_entry.bind('<Return>', self._on_id_enter)
            self.id_entry.bind('<FocusOut>', self._on_id_focus_out)
        
        # Trace variable changes for external updates
        self.id_var.trace_add('write', self._on_id_var_changed)
        self.name_var.trace_add('write', self._on_name_var_changed)
        
    def _show_placeholder(self):
        """Show placeholder text"""
        if not self.name_var.get():
            self.name_entry.config(fg='#9ca3af')
            self._is_syncing = True
            self.name_var.set(self.placeholder)
            self._is_syncing = False
            
    def _hide_placeholder(self):
        """Hide placeholder text"""
        if self.name_var.get() == self.placeholder:
            self._is_syncing = True
            self.name_var.set('')
            self._is_syncing = False
        self.name_entry.config(fg='#111827')
        
    def _on_focus_in(self, event=None):
        """Handle focus in"""
        self._hide_placeholder()
        
    def _on_focus_out(self, event=None):
        """Handle focus out"""
        if not self.name_var.get():
            self._show_placeholder()
        # Delay closing to allow click events to register and check where focus went
        self.after(150, self._check_focus_lost)
        
    def _on_name_key(self, event=None):
        """Handle key press in name entry - trigger autocomplete"""
        if event and event.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R'):
            return
            
        # Cancel previous debounce
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
            
        # Schedule new search
        self._debounce_id = self.after(self.DEBOUNCE_MS, self._do_autocomplete)
        
    def _do_autocomplete(self):
        """Perform autocomplete search"""
        search_term = self.name_var.get()
        
        if not search_term or search_term == self.placeholder:
            self._close_dropdown()
            return
            
        # Get matching items
        try:
            results = self.data_source(search_term)[:self.MAX_AUTOCOMPLETE_ITEMS]
        except Exception as e:
            print(f"SmartLookup data_source error: {e}")
            results = []
            
        if results:
            self._show_dropdown(results, is_autocomplete=True)
        else:
            self._close_dropdown()
            
    def _on_id_key(self, event=None):
        """Handle key press in ID entry"""
        if event and event.keysym in ('Return', 'Tab'):
            return
        # Debounce ID lookup too
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(self.DEBOUNCE_MS, self._lookup_by_id)
        
    def _on_id_enter(self, event=None):
        """Handle Enter in ID field"""
        self._lookup_by_id()
        
    def _on_id_focus_out(self, event=None):
        """Handle focus out from ID field"""
        self._lookup_by_id()
        
    # ... (other methods maintained by simple replacement context match if I limit lines?)
    # I'll rely on the surrounding context matching to be safe.
    # Actually, I'll limit the replacement chunk to just _on_focus_out IF possible, but I want to add bindings too which is far away.
    # I'll use multiple chunks.
    
    # Chunk 1: _on_focus_out
        
    def _on_name_key(self, event=None):
        """Handle key press in name entry - trigger autocomplete"""
        if event and event.keysym in ('Up', 'Down', 'Return', 'Escape', 'Tab', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R'):
            return
            
        # Cancel previous debounce
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
            
        # Schedule new search
        self._debounce_id = self.after(self.DEBOUNCE_MS, self._do_autocomplete)
        
    def _do_autocomplete(self):
        """Perform autocomplete search"""
        search_term = self.name_var.get()
        
        if not search_term or search_term == self.placeholder:
            self._close_dropdown()
            return
            
        # Get matching items
        try:
            results = self.data_source(search_term)[:self.MAX_AUTOCOMPLETE_ITEMS]
        except Exception as e:
            print(f"SmartLookup data_source error: {e}")
            results = []
            
        if results:
            self._show_dropdown(results, is_autocomplete=True)
        else:
            self._close_dropdown()
            
    def _on_id_key(self, event=None):
        """Handle key press in ID entry"""
        if event and event.keysym in ('Return', 'Tab'):
            return
        # Debounce ID lookup too
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(self.DEBOUNCE_MS, self._lookup_by_id)
        
    def _on_id_enter(self, event=None):
        """Handle Enter in ID field"""
        self._lookup_by_id()
        
    def _on_id_focus_out(self, event=None):
        """Handle focus out from ID field"""
        self._lookup_by_id()
        
    def _lookup_by_id(self):
        """Look up item by ID and fill name"""
        if self._is_syncing:
            return
            
        id_value = self.id_var.get().strip()
        if not id_value:
            return
            
        # Search for exact ID match
        try:
            all_data = self.data_source("")
            for item_id, item_name, extra_data in all_data:
                if item_id.lower() == id_value.lower():
                    self._select_item(item_id, item_name, extra_data, from_id=True)
                    return
        except Exception as e:
            print(f"SmartLookup ID lookup error: {e}")
            
        # ID not found - show validation error
        self._show_validation_error()
        
    def _on_id_var_changed(self, *args):
        """Handle external changes to ID variable"""
        if self._is_syncing:
            return
        # Trigger lookup if ID changed externally
        self.after(100, self._lookup_by_id)
        
    def _on_name_var_changed(self, *args):
        """Handle external changes to name variable"""
        pass  # Name changes handled by autocomplete
        
    def _on_arrow_down(self, event=None):
        """Handle down arrow - open/navigate dropdown"""
        if self._dropdown_window:
            self._selected_index = min(self._selected_index + 1, len(self._data_cache) - 1)
            self._highlight_selection()
        else:
            self._toggle_dropdown()
        return 'break'
        
    def _on_arrow_up(self, event=None):
        """Handle up arrow - navigate dropdown"""
        if self._dropdown_window:
            self._selected_index = max(self._selected_index - 1, 0)
            self._highlight_selection()
        return 'break'
        
    def _on_enter(self, event=None):
        """Handle Enter - select current item"""
        if self._dropdown_window and self._selected_index >= 0:
            if self._selected_index < len(self._data_cache):
                item = self._data_cache[self._selected_index]
                self._select_item(item[0], item[1], item[2] if len(item) > 2 else {})
        return 'break'
        
    def _on_escape(self, event=None):
        """Handle Escape - close dropdown"""
        self._close_dropdown()
        return 'break'
        
    def _on_tab(self, event=None):
        """Handle Tab - select and move focus"""
        if self._dropdown_window and self._selected_index >= 0:
            if self._selected_index < len(self._data_cache):
                item = self._data_cache[self._selected_index]
                self._select_item(item[0], item[1], item[2] if len(item) > 2 else {})
        self._close_dropdown()
        
    def _toggle_dropdown(self):
        """Toggle dropdown visibility"""
        if self._dropdown_window:
            self._close_dropdown()
        else:
            self._open_full_dropdown()
            
    def _open_full_dropdown(self):
        """Open dropdown with all items"""
        try:
            all_data = self.data_source("")[:self.MAX_DROPDOWN_ITEMS]
            if all_data:
                self._show_dropdown(all_data, is_autocomplete=False)
        except Exception as e:
            print(f"SmartLookup dropdown error: {e}")
            
    def _show_dropdown(self, items: List[Tuple], is_autocomplete: bool = False):
        """Show dropdown with items"""
        self._close_dropdown()
        self._data_cache = items
        self._selected_index = 0
        
        # Create dropdown window
        self._dropdown_window = tk.Toplevel(self)
        self._dropdown_window.wm_overrideredirect(True)  # No window decorations
        self._dropdown_window.wm_attributes('-topmost', True)
        
        # Position below entry
        x = self.name_entry.winfo_rootx()
        y = self.name_entry.winfo_rooty() + self.name_entry.winfo_height() + 2
        width = max(self.name_entry.winfo_width() + 30, 250)
        
        # Calculate height
        item_height = 32
        max_visible = 8
        height = min(len(items), max_visible) * item_height + 4
        
        self._dropdown_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Container with border
        container = tk.Frame(
            self._dropdown_window,
            bg='white',
            bd=1,
            relief='solid',
            highlightthickness=1,
            highlightbackground='#d1d5db'
        )
        container.pack(fill='both', expand=True)
        
        # Scrollable canvas
        canvas = tk.Canvas(container, bg='white', highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        
        self._items_frame = tk.Frame(canvas, bg='white')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=self._items_frame, anchor='nw')
        
        # Create item widgets
        self._item_widgets = []
        for i, item in enumerate(items):
            item_id = item[0]
            item_name = item[1]
            extra_data = item[2] if len(item) > 2 else {}
            
            # Item frame
            item_frame = tk.Frame(self._items_frame, bg='white', cursor='hand2')
            item_frame.pack(fill='x', padx=2, pady=1)
            
            # Main label (name)
            name_lbl = tk.Label(
                item_frame,
                text=item_name,
                font=("Segoe UI", 10),
                bg='white',
                fg='#111827',
                anchor='w',
                padx=10,
                pady=4
            )
            name_lbl.pack(side='left', fill='x', expand=True)
            
            # ID label (smaller, gray)
            id_lbl = tk.Label(
                item_frame,
                text=item_id,
                font=("Segoe UI", 9),
                bg='white',
                fg='#6b7280',
                anchor='e',
                padx=10,
                pady=4
            )
            id_lbl.pack(side='right')
            
            # Bind click
            for widget in (item_frame, name_lbl, id_lbl):
                widget.bind('<Button-1>', lambda e, idx=i: self._on_item_click(idx))
                widget.bind('<Double-Button-1>', lambda e, idx=i: self._on_item_click(idx))
                widget.bind('<Enter>', lambda e, idx=i: self._on_item_hover(idx))
            
            self._item_widgets.append((item_frame, name_lbl, id_lbl))
        
        # Update scroll region
        self._items_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox('all'))
        
        # Pack canvas and scrollbar
        canvas.pack(side='left', fill='both', expand=True)
        if len(items) > max_visible:
            scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        # Highlight first item
        self._highlight_selection()
        
        # Close on click outside
        self._dropdown_window.bind('<FocusOut>', lambda e: self.after(100, self._check_focus_lost))
        
    def _check_focus_lost(self):
        """Check if focus is lost and close dropdown"""
        try:
            focused = self.focus_get()
            if focused and (focused == self.name_entry or 
                          (self._dropdown_window and focused.winfo_toplevel() == self._dropdown_window)):
                return
        except:
            pass
        self._close_dropdown()
        
    def _on_item_click(self, index: int):
        """Handle item click"""
        if 0 <= index < len(self._data_cache):
            item = self._data_cache[index]
            self._select_item(item[0], item[1], item[2] if len(item) > 2 else {})
            
    def _on_item_hover(self, index: int):
        """Handle item hover"""
        self._selected_index = index
        self._highlight_selection()
        
    def _highlight_selection(self):
        """Highlight the currently selected item"""
        if not self._item_widgets:
            return
            
        for i, (frame, name_lbl, id_lbl) in enumerate(self._item_widgets):
            if i == self._selected_index:
                frame.configure(bg='#3b82f6')
                name_lbl.configure(bg='#3b82f6', fg='white')
                id_lbl.configure(bg='#3b82f6', fg='#bfdbfe')
            else:
                frame.configure(bg='white')
                name_lbl.configure(bg='white', fg='#111827')
                id_lbl.configure(bg='white', fg='#6b7280')
                
    def _select_item(self, item_id: str, item_name: str, extra_data: Dict = None, from_id: bool = False):
        """Select an item and update bound variables"""
        self._is_syncing = True
        
        # Update variables
        self.id_var.set(item_id)
        self.name_var.set(item_name)
        
        # Store selection
        self._last_valid_selection = (item_id, item_name, extra_data or {})
        
        # Update entry styling
        self.name_entry.config(fg='#111827')
        self._clear_validation_error()
        
        self._is_syncing = False
        
        # Close dropdown
        self._close_dropdown()
        
        # Call callback
        if self.on_select_callback:
            try:
                self.on_select_callback(item_id, item_name, extra_data or {})
            except Exception as e:
                print(f"SmartLookup on_select callback error: {e}")
                
    def _close_dropdown(self):
        """Close the dropdown window"""
        if self._dropdown_window:
            try:
                self._dropdown_window.destroy()
            except:
                pass
            self._dropdown_window = None
            self._item_widgets = []
            self._selected_index = -1
            
    def _show_validation_error(self):
        """Show validation error styling"""
        self.name_entry.config(bg='#fef2f2')
        if hasattr(self, 'id_entry'):
            self.id_entry.configure(style='Error.TEntry')
            
    def _clear_validation_error(self):
        """Clear validation error styling"""
        self.name_entry.config(bg='white')
        
    # Public API
    
    def get_value(self) -> Tuple[str, str]:
        """Get current ID and Name values"""
        return (self.id_var.get(), self.name_var.get())
        
    def set_value(self, item_id: str = None, item_name: str = None):
        """Set the field value"""
        self._is_syncing = True
        if item_id is not None:
            self.id_var.set(item_id)
        if item_name is not None:
            self.name_var.set(item_name)
            self.name_entry.config(fg='#111827')
        self._is_syncing = False
        
    def clear(self):
        """Clear the field"""
        self._is_syncing = True
        self.id_var.set('')
        self.name_var.set('')
        self._show_placeholder()
        self._last_valid_selection = None
        self._is_syncing = False
        
    def get_extra_data(self) -> Dict:
        """Get extra data from last selection"""
        if self._last_valid_selection:
            return self._last_valid_selection[2]
        return {}
        
    def refresh_data(self):
        """Refresh data from source (clears any cache in the source)"""
        self._data_cache = []
        

class SmartLookupFieldWithID(ttk.Frame):
    """
    Combined widget showing both ID and Name fields with synchronization.
    Useful when both ID and Name should be visible and editable.
    """
    
    def __init__(
        self,
        parent,
        label: str,
        data_source: Callable,
        id_label: str = "ID",
        name_label: str = "Name",
        on_select: Callable = None
    ):
        super().__init__(parent)
        
        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        
        # ID field row
        id_frame = ttk.Frame(self)
        id_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(id_frame, text=id_label, width=15, anchor='e').pack(side='left', padx=(0, 10))
        self.id_entry = ttk.Entry(id_frame, textvariable=self.id_var, width=20)
        self.id_entry.pack(side='left')
        
        # Name lookup row
        name_frame = ttk.Frame(self)
        name_frame.pack(fill='x')
        
        ttk.Label(name_frame, text=name_label, width=15, anchor='e').pack(side='left', padx=(0, 10))
        
        self.lookup = SmartLookupField(
            name_frame,
            label="",
            data_source=data_source,
            id_var=self.id_var,
            name_var=self.name_var,
            on_select=on_select
        )
        self.lookup.pack(side='left', fill='x', expand=True)
        
    def get_id(self) -> str:
        return self.id_var.get()
        
    def get_name(self) -> str:
        return self.name_var.get()
        
    def set_value(self, item_id: str, item_name: str):
        self.id_var.set(item_id)
        self.name_var.set(item_name)
