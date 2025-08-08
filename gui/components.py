# gui/components.py
import tkinter as tk
from tkinter import ttk
import os
import math
from datetime import datetime
from constants import DAYS, AUDIO_DIR

class ClockFace(tk.Canvas):
    def __init__(self, parent, size=150, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, **kwargs)
        self.size = size
        self.center = size // 2
        self.radius = size // 2 - 10
        
        # Draw clock face
        self._draw_clock_face()
        
        # Update time every second
        self._update_time()
        
    def _draw_clock_face(self):
        """Draw the clock face with hour markers"""
        # Draw outer circle
        self.create_oval(
            self.center - self.radius, 
            self.center - self.radius,
            self.center + self.radius, 
            self.center + self.radius,
            fill="white", 
            outline="#2c3e50", 
            width=2
        )
        
        # Draw hour markers
        for i in range(12):
            angle = i * 30  # 30 degrees per hour
            # Convert angle to radians
            rad = math.radians(angle - 90)  # -90 to start from top
            
            # Calculate marker positions
            if i % 3 == 0:  # Hour markers
                inner_radius = self.radius - 15
                width = 3
            else:  # Minute markers
                inner_radius = self.radius - 8
                width = 1
                
            x1 = self.center + inner_radius * math.cos(rad)
            y1 = self.center + inner_radius * math.sin(rad)
            x2 = self.center + self.radius * math.cos(rad)
            y2 = self.center + self.radius * math.sin(rad)
            
            self.create_line(x1, y1, x2, y2, fill="#2c3e50", width=width)
        
        # Draw center dot
        self.create_oval(
            self.center - 5, 
            self.center - 5,
            self.center + 5, 
            self.center + 5,
            fill="#2c3e50"
        )
        
        # Create clock hands
        self.hour_hand = self.create_line(
            self.center, self.center,
            self.center, self.center - self.radius * 0.5,
            fill="#2c3e50", width=4, capstyle="round"
        )
        
        self.minute_hand = self.create_line(
            self.center, self.center,
            self.center, self.center - self.radius * 0.7,
            fill="#2c3e50", width=3, capstyle="round"
        )
        
        self.second_hand = self.create_line(
            self.center, self.center,
            self.center, self.center - self.radius * 0.8,
            fill="#e74c3c", width=1, capstyle="round"
        )
    
    def _update_time(self):
        """Update the clock hands to show current time"""
        now = datetime.now()
        
        # Calculate angles
        second_angle = (now.second * 6) - 90  # 6 degrees per second
        minute_angle = (now.minute * 6 + now.second * 0.1) - 90  # 6 degrees per minute
        hour_angle = (now.hour % 12 * 30 + now.minute * 0.5) - 90  # 30 degrees per hour
        
        # Update hand positions
        self._update_hand(self.second_hand, second_angle, self.radius * 0.8)
        self._update_hand(self.minute_hand, minute_angle, self.radius * 0.7)
        self._update_hand(self.hour_hand, hour_angle, self.radius * 0.5)
        
        # Schedule next update
        self.after(1000, self._update_time)
    
    def _update_hand(self, hand, angle, length):
        """Update a clock hand position"""
        rad = math.radians(angle)
        x = self.center + length * math.cos(rad)
        y = self.center + length * math.sin(rad)
        self.coords(hand, self.center, self.center, x, y)


class ScheduleTable(tk.Frame):
    def __init__(self, parent, rows=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.rows = rows
        self.cells = {}  # Store cell widgets
        
        # Create table structure
        self._create_table()
        
    def _create_table(self):
        """Create the schedule table structure"""
        # Configure grid columns
        for col in range(len(DAYS)):
            self.grid_columnconfigure(col, weight=1, uniform="days")
        
        # Create rows
        for row in range(self.rows):
            self.grid_rowconfigure(row, weight=1)
            
            # Create cells for each day
            for col, day in enumerate(DAYS):
                # Create frame for cell
                cell_frame = tk.Frame(self, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                
                # Create text widget for content
                text_widget = tk.Text(
                    cell_frame, 
                    height=1, 
                    width=15, 
                    bg="white", 
                    fg="#2c3e50",
                    font=("Arial", 9),
                    relief="flat",
                    highlightthickness=0,
                    wrap="none"
                )
                text_widget.pack(fill="both", expand=True, padx=2, pady=2)
                
                # Store reference to the text widget
                self.cells[(row, col)] = text_widget
    
    def update_data(self, schedules):
        """Update table with schedule data"""
        # Clear all cells
        for widget in self.cells.values():
            widget.delete(1.0, tk.END)
        
        # Populate with schedule data
        for day_idx, day in enumerate(DAYS):
            if day in schedules:
                for row_idx, (time_str, audio_path) in enumerate(schedules[day]):
                    if row_idx < self.rows:
                        # Get filename from path
                        filename = os.path.basename(audio_path)
                        # Format display text
                        display_text = f"{time_str} - {filename}"
                        
                        # Update cell
                        cell = self.cells.get((row_idx, day_idx))
                        if cell:
                            cell.insert(1.0, display_text)
    
    def get_cell_count(self):
        """Get the total number of cells in the table"""
        return len(self.cells)


class StatusBar(tk.Frame):
    def __init__(self, parent, bg_color, text_color, **kwargs):
        super().__init__(parent, bg=bg_color, height=25, **kwargs)
        self.pack_propagate(False)
        
        # Status label
        self.status_label = tk.Label(
            self,
            text="Ready",
            bg=bg_color,
            fg=text_color,
            font=("Arial", 9),
            anchor="w",
            padx=10
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Clock label
        self.clock_label = tk.Label(
            self,
            text="",
            bg=bg_color,
            fg=text_color,
            font=("Arial", 9),
            anchor="e",
            padx=10
        )
        self.clock_label.pack(side="right")
        
        # Update clock
        self._update_clock()
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message)
    
    def _update_clock(self):
        """Update clock display"""
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self._update_clock)