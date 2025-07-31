# gui/components.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import math
import os
from constants import DAYS
from logger import log_error

class ClockFace(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=100, height=100, bg='white', highlightthickness=0, **kwargs)
        self.create_oval(5, 5, 95, 95, width=2)
        self.hands = [
            self.create_line(50, 50, 50, 20, width=3, fill='black'),  # jam
            self.create_line(50, 50, 50, 15, width=2, fill='blue'),   # menit
            self.create_line(50, 50, 50, 10, width=1, fill='red')     # detik
        ]
        self.tick()

    def tick(self):
        now = datetime.now()
        s = now.second
        m = now.minute + s / 60
        h = now.hour % 12 + m / 60
        angle_s = 90 - s * 6
        angle_m = 90 - m * 6
        angle_h = 90 - h * 30
        self._update_hand(self.hands[2], angle_s, 40, 'red')
        self._update_hand(self.hands[1], angle_m, 35, 'blue')
        self._update_hand(self.hands[0], angle_h, 25, 'black')
        self.after(1000, self.tick)

    def _update_hand(self, hand, angle, length, color):
        x = 50 + length * math.cos(math.radians(angle))
        y = 50 - length * math.sin(math.radians(angle))
        self.coords(hand, 50, 50, x, y)


class ScheduleTable(tk.Frame):
    def __init__(self, parent, rows=10, **kwargs):
        super().__init__(parent, **kwargs)
        self.rows = rows
        self.entries = []
        self._setup_table()

    def _setup_table(self):
        # Header dengan nama hari
        for col, day in enumerate(DAYS):
            tk.Label(self, text=day, relief="groove", width=15, bg="lightgray", 
                     font=("Arial", 10, "bold")).grid(row=0, column=col, sticky="nsew")

        # Grid jadwal
        for row in range(self.rows):
            row_entries = []
            for col in range(len(DAYS)):
                entry = tk.Entry(self, width=15, relief="groove", bg="lightgreen")
                entry.grid(row=row+1, column=col, sticky="nsew")
                row_entries.append(entry)
            self.entries.append(row_entries)

    def clear(self):
        """Clear all entries"""
        for row in self.entries:
            for entry in row:
                entry.delete(0, tk.END)

    def update_schedule(self, schedules):
        """Update schedule display"""
        try:
            self.clear()
            day_map = {day: idx for idx, day in enumerate(DAYS)}
            
            for day, day_idx in day_map.items():
                day_schedules = schedules.get(day, [])
                for row_idx, (schedule_time, path) in enumerate(day_schedules):
                    if row_idx < self.rows:
                        filename = os.path.basename(path)
                        self.entries[row_idx][day_idx].insert(0, f"{schedule_time} - {filename}")
        except Exception as e:
            log_error(f"Gagal update schedule table: {e}")


class StatusBar(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.time_label = tk.Label(
            self,
            text="",
            relief="sunken",
            anchor="e",
            font=("Courier", 9),
            bg="lightgray",
            fg="black"
        )
        self.time_label.pack(side="bottom", fill="x", padx=1, pady=1)
        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("  %H:%M:%S | %d-%m-%Y"))
        self.after(1000, self.update_time)