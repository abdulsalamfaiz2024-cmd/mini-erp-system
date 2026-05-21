"""
Dynamic Top Action Bar Component
Displays contextual actions for the current page
"""

import tkinter as tk
from tkinter import ttk
from ui.styles import Theme


class TopBar(ttk.Frame):
    """
    Dynamic action bar that displays page-specific actions.
    Populated by each page with relevant buttons.
    """
    
    def __init__(self, parent):
        super().__init__(parent, style='TopBar.TFrame', height=60)
        self.pack_propagate(False)
        
        # Page title container
        self.title_frame = tk.Frame(self, bg='white')
        self.title_frame.pack(side='left', fill='y', padx=20, pady=10)
        
        self.title_label = ttk.Label(
            self.title_frame,
            text="",
            font=('Segoe UI', 16, 'bold'),
            style='TopBar.TLabel'
        )
        self.title_label.pack(side='left')
        
        # Actions container (right-aligned)
        self.actions_frame = tk.Frame(self, bg='white')
        self.actions_frame.pack(side='right', fill='y', padx=20, pady=10)
        
        self.action_buttons = []
    
    def set_page_title(self, title):
        """Set the page title"""
        self.title_label.configure(text=title)
    
    def clear_actions(self):
        """Remove all action buttons"""
        for btn in self.action_buttons:
            btn.destroy()
        self.action_buttons.clear()
    
    def add_action(self, text, command, style='Primary.TButton', icon=None, 
                   enabled=True, tooltip=None):
        """
        Add an action button to the bar.
        
        Args:
            text: Button text
            command: Callback function
            style: Button style (Primary, Success, Danger, Secondary)
            icon: Optional emoji/unicode icon
            enabled: Whether button is enabled
            tooltip: Tooltip text explaining why disabled
        
        Returns:
            The created button widget
        """
        display_text = f"{icon} {text}" if icon else text
        
        btn = ttk.Button(
            self.actions_frame,
            text=display_text,
            command=command,
            style=style
        )
        btn.pack(side='left', padx=5)
        
        if not enabled:
            btn.configure(state='disabled')
            if tooltip:
                # Create tooltip (simplified - could use full tooltip widget)
                self._create_tooltip(btn, tooltip)
        
        self.action_buttons.append(btn)
        return btn
    
    def add_separator(self):
        """Add a visual separator between button groups"""
        sep = tk.Frame(self.actions_frame, bg=Theme.BORDER_LIGHT, width=1)
        sep.pack(side='left', fill='y', padx=10, pady=5)
        self.action_buttons.append(sep)
    
    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for disabled buttons"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background='#ffffe0',
                relief='solid',
                borderwidth=1,
                font=('Segoe UI', 9),
                padx=5,
                pady=3
            )
            label.pack()
            
            # Auto-destroy after 2 seconds
            tooltip.after(2000, tooltip.destroy)
        
        widget.bind('<Enter>', show_tooltip)
    
    def set_actions(self, actions_config):
        """
        Set all actions at once from a configuration.
        
        Args:
            actions_config: List of dicts with keys: text, command, style, icon, enabled, tooltip
        
        Example:
            topbar.set_actions([
                {'text': 'New Order', 'command': self.new_order, 'icon': '➕'},
                {'text': 'Submit', 'command': self.submit, 'style': 'Success.TButton'},
                {'type': 'separator'},
                {'text': 'Export', 'command': self.export, 'icon': '📑'},
            ])
        """
        self.clear_actions()
        
        for action in actions_config:
            if action.get('type') == 'separator':
                self.add_separator()
            else:
                self.add_action(
                    text=action['text'],
                    command=action['command'],
                    style=action.get('style', 'Primary.TButton'),
                    icon=action.get('icon'),
                    enabled=action.get('enabled', True),
                    tooltip=action.get('tooltip')
                )


# Configure custom style for topbar
def configure_topbar_style():
    style = ttk.Style()
    style.configure('TopBar.TFrame', background='white', relief='solid', borderwidth=1)
    style.configure('TopBar.TLabel', background='white')
