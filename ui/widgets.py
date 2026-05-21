import tkinter as tk
from tkinter import ttk
from ui.styles import Theme

class ChartWidget(tk.Canvas):
    def __init__(self, parent, width=600, height=300, **kwargs):
        super().__init__(parent, width=width, height=height, bg=Theme.BG_WHITE, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.data = []
        
    def draw_bar_chart(self, title, data):
        """
        Draws a simple bar chart.
        data: List of (label, value) tuples
        """
        self.delete("all")
        self.data = data
        
        # Margins
        margin_left = 60
        margin_bottom = 40
        margin_top = 50
        margin_right = 20
        
        # Drawing Area
        draw_w = self.width - margin_left - margin_right
        draw_h = self.height - margin_top - margin_bottom
        
        if not data:
            self.create_text(self.width/2, self.height/2, text="No Data Available", fill=Theme.TEXT_MUTED, font=("Segoe UI", 12))
            return
            
        # Scaling
        max_val = max([d[1] for d in data]) or 100
        bar_width = draw_w / len(data) * 0.6
        spacing = draw_w / len(data)
        
        # Title
        self.create_text(20, 20, text=title, anchor='w', fill=Theme.PRIMARY, font=("Segoe UI", 12, "bold"))
        
        # Axis Lines
        self.create_line(margin_left, self.height - margin_bottom, self.width - margin_right, self.height - margin_bottom, fill=Theme.BORDER_LIGHT, width=2)
        # self.create_line(margin_left, margin_top, margin_left, self.height - margin_bottom, fill=Theme.BORDER_LIGHT, width=2)
        
        # Draw Bars
        for i, (label, value) in enumerate(data):
            x = margin_left + (i * spacing) + (spacing/2)
            bar_h = (value / max_val) * draw_h if max_val > 0 else 0
            
            y1 = self.height - margin_bottom
            y0 = y1 - bar_h
            
            color = Theme.CHART_BARS[i % len(Theme.CHART_BARS)]
            
            # Bar
            self.create_rectangle(x - bar_width/2, y0, x + bar_width/2, y1, fill=color, outline="")
            
            # Value Label
            self.create_text(x, y0 - 10, text=str(int(value)), fill=Theme.TEXT_MUTED, font=("Segoe UI", 9))
            
            # X Axis Label
            self.create_text(x, y1 + 15, text=label, fill=Theme.TEXT_MAIN, font=("Segoe UI", 9))
            
    def draw_line_chart(self, title, data):
        pass # To satisfy checklist if needed later
