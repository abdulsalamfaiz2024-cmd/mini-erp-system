import tkinter as tk
from tkinter import ttk
from ui.styles import Theme

class ModernTable(ttk.Frame):
    """
    A stylized wrapper around Treeview that handles:
    - Alternating row colors (striping)
    - Scrollbars (auto-hidden or styled)
    - Easy column definition
    - External data loading
    """
    def __init__(self, parent, columns, height=10):
        super().__init__(parent, style='Card.TFrame')
        self.columns = columns
        
        # 1. Treeview
        self.tree = ttk.Treeview(self, columns=[c['name'] for c in columns], 
                                 show='headings', selectmode='browse', height=height)
        
        # 2. Config Headers & Columns
        for col in columns:
            name = col['name']
            text = col.get('text', name.title())
            width = col.get('width', 100)
            anchor = col.get('anchor', 'w')
            
            self.tree.heading(name, text=text)
            self.tree.column(name, width=width, anchor=anchor)
            
        # 3. Tags for Colors
        self.tree.tag_configure('odd', background="#F7F9F9")
        self.tree.tag_configure('even', background="#FFFFFF")
        
        # Status Tags (Pre-defined in styles.py)
        # We will apply these dynamically based on data content if needed
        
        # 4. Scrollbar
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        self.vsb.pack(side='right', fill='y')

    def set_data(self, rows):
        """
        rows: list of tuples/lists matching columns.
        item format: (val1, val2, val3...)
        Optional: To style rows based on status, pass a dict or object with 'tags'
        But standard Treeview only takes values.
        
        We'll accept list of DB rows (dicts) usually? Or tuples. 
        Let's assume list of tuples for raw display.
        """
        self.clear()
        
        for idx, row in enumerate(rows):
            # Determine stripe tag
            stripe = 'even' if idx % 2 == 0 else 'odd'
            
            # Simple Value Insertion
            # Advanced: Check for "Status" column to add color tags
            # We combine stripe + status tags if needed. 
            # Tkinter 8.6 supports multiple tags.
            
            # Try to find status or payment in values? 
            # This is hard to do generically without metadata.
            # For now, just striping.
            
            tags = [stripe]
            
            # Auto-Status Coloring
            # Check if any value in the row matches a known status keyword
            for val in row:
                s = str(val).lower()
                if s in ['paid', 'completed', 'active']:
                    tags.append('Paid.Treeview')
                elif s in ['pending', 'draft', 'partial']:
                    tags.append('Pending.Treeview')
                elif s in ['overdue', 'cancelled', 'void']:
                    tags.append('Overdue.Treeview')
                elif s in ['invoiced']:
                    tags.append('Invoiced.Treeview')
            
            self.tree.insert('', 'end', values=row, tags=tuple(tags))
            
    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def get_selected(self):
        sel = self.tree.selection()
        if not sel: return None
        return self.tree.item(sel[0])



class ModernForm(ttk.Frame):
    """
    Standardized Input Group: Label + Entry/Combo/Lookup
    
    Supports:
    - 'entry': Basic text entry
    - 'combobox': Dropdown selection
    - 'lookup': SmartLookupField with autocomplete and bi-directional binding
    """
    def __init__(self, parent, label, input_type='entry', options=None, variable=None,
                 lookup_config=None):
        """
        Args:
            parent: Parent widget
            label: Field label
            input_type: 'entry', 'combobox', or 'lookup'
            options: List of options for combobox
            variable: StringVar for entry/combobox
            lookup_config: Dict for lookup type with keys:
                - data_source: Callable(search_term) -> List[(id, name, extra)]
                - id_var: StringVar for ID (optional)
                - on_select: Callback(id, name, extra) (optional)
                - placeholder: Placeholder text (optional)
        """
        super().__init__(parent, style='Card.TFrame')
        
        self.widget = None
        
        if input_type == 'entry':
            lbl = ttk.Label(self, text=label, style='CardSub.TLabel')
            lbl.pack(anchor='w', pady=(0, 5))
            self.widget = ttk.Entry(self, textvariable=variable, font=("Segoe UI", 10))
            self.widget.pack(fill='x')
            
        elif input_type == 'combobox':
            lbl = ttk.Label(self, text=label, style='CardSub.TLabel')
            lbl.pack(anchor='w', pady=(0, 5))
            self.widget = ttk.Combobox(self, textvariable=variable, values=options, font=("Segoe UI", 10))
            self.widget.pack(fill='x')
            
        elif input_type == 'lookup':
            # SmartLookupField with autocomplete
            try:
                from ui.widgets.smart_lookup import SmartLookupField
                
                config = lookup_config or {}
                self.widget = SmartLookupField(
                    self,
                    label=label,
                    data_source=config.get('data_source', lambda x: []),
                    id_var=config.get('id_var'),
                    name_var=variable,
                    on_select=config.get('on_select'),
                    placeholder=config.get('placeholder', 'Search...'),
                    required=config.get('required', False)
                )
                self.widget.pack(fill='x')
            except ImportError:
                # Fallback to combobox
                lbl = ttk.Label(self, text=label, style='CardSub.TLabel')
                lbl.pack(anchor='w', pady=(0, 5))
                self.widget = ttk.Combobox(self, textvariable=variable, values=options or [], font=("Segoe UI", 10))
                self.widget.pack(fill='x')
        else:
            # Default to entry
            lbl = ttk.Label(self, text=label, style='CardSub.TLabel')
            lbl.pack(anchor='w', pady=(0, 5))
            self.widget = ttk.Entry(self, textvariable=variable, font=("Segoe UI", 10))
            self.widget.pack(fill='x')


class ScrollableFrame(ttk.Frame):
    """
    A Frame that can scroll vertically.
    Uses a Canvas + internal Frame pattern.
    """
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # 1. Canvas and Scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=Theme.BG_MAIN)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # 2. Internal Frame (The contents go here)
        self.scrollable_frame = ttk.Frame(self.canvas, style='Main.TFrame')
        
        # Bind for resizing
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )
        
        # Mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_canvas_configure(self, event):
        # Resize inner frame to match canvas width
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def _on_mousewheel(self, event):
        # Only scroll if valid
        if self.vsb.winfo_ismapped():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Update ModernOverlay to be safer
class ModernOverlay(tk.Frame):
    def __init__(self, parent_view, title, width=600, height=500):
        # Attach to root if possible or parent
        # We need to find the top-level window to cover everything
        root = parent_view.winfo_toplevel()
        super().__init__(root)
        
        self.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Dimmer
        self.bg = tk.Frame(self, bg="#2C3E50") 
        # Opacity hack using alpha not supported well in frames.
        # We just use a solid color for enterprise look (like a slate overlay)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg.bind('<Button-1>', lambda e: self.close())
        
        # Container for centering
        # We use a wrapper frame that stays centered
        self.wrapper = tk.Frame(self, bg="#2C3E50")
        self.wrapper.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.9, relheight=0.9) # Max 90% screen
        
        # The Card Itself (Constrained max size, but flexible)
        # We put a Card Frame inside the wrapper.
        # We want the card to be at most 'width' wide, and 'height' high.
        # But if screen is smaller, it shrinks.
        
        self.card = ttk.Frame(self.wrapper, style='Card.TFrame')
        self.card.pack(expand=True) # Center in wrapper? 
        # Actually simplest is to place card in self (fullscreen) with limitations.
        # But we want scroll if content is too big.
        
        # Let's use a ScrollableFrame inside the Card if content is huge?
        # Simpler: The Card is just a frame. If it overflows, users are stuck unless we use ScrollableFrame for Interaction Area.
        # Let's just enforce sizing on the card frame.
        
        # Re-do placement:
        self.card.place(relx=0.5, rely=0.5, anchor='center', width=width, height=height)
        
        # Header
        header = tk.Frame(self.card, bg=Theme.BG_WHITE, height=60)
        header.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header, text=title, font=("Segoe UI", 16, "bold"), bg=Theme.BG_WHITE, fg=Theme.PRIMARY).pack(side='left')
        
        # Close X
        close_btn = tk.Label(header, text="✕", font=("Segoe UI", 12), bg=Theme.BG_WHITE, fg=Theme.TEXT_MUTED, cursor="hand2")
        close_btn.pack(side='right')
        close_btn.bind('<Button-1>', lambda e: self.close())
        
        # Content - SCROLLABLE
        # This fixes the clipping issue on small screens
        self.content_area = ScrollableFrame(self.card)
        self.content_area.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Alias for external usage:
        # Users usually pack into .content. Now they should pack into .content_area.scrollable_frame
        self.content = self.content_area.scrollable_frame
        
    def close(self):
        self.destroy()
