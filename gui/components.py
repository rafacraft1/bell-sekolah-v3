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
        # Konfigurasi grid agar responsive
        for col in range(len(DAYS)):
            self.grid_columnconfigure(col, weight=1, uniform="schedule_cols")
        
        for row in range(self.rows):
            self.grid_rowconfigure(row, weight=1, uniform="schedule_rows")
        
        # Grid jadwal dengan styling yang lebih baik
        for row in range(self.rows):
            row_entries = []
            for col in range(len(DAYS)):
                # Alternate row colors for better readability
                bg_color = "#f8f9fa" if row % 2 == 0 else "#e9ecef"
                
                entry = tk.Entry(
                    self, 
                    width=15, 
                    relief="flat", 
                    bg=bg_color,
                    font=("Arial", 9),
                    highlightthickness=1,
                    highlightbackground="#dee2e6",
                    highlightcolor="#adb5bd",
                    selectbackground="#3498db",
                    selectforeground="white"
                )
                entry.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                row_entries.append(entry)
            self.entries.append(row_entries)

    def update_font_size(self, base_size):
        """Update font size untuk semua entries"""
        for row_entries in self.entries:
            for entry in row_entries:
                current_font = entry.cget("font")
                if isinstance(current_font, tuple):
                    font_family = current_font[0]
                    new_font = (font_family, base_size)
                else:
                    new_font = ("Arial", base_size)
                entry.config(font=new_font)

    def get_content_width(self):
        """Hitung lebar konten tabel"""
        if not self.entries:
            return len(DAYS) * 120  # Default width per column
        
        # Hitung lebar berdasarkan jumlah kolom dan lebar entry
        total_width = 0
        if self.entries[0]:
            # Gunakan lebar minimum yang wajar per kolom
            min_col_width = 120  # Minimum lebar per kolom
            total_width = len(DAYS) * min_col_width
        
        return max(total_width, len(DAYS) * 120)  # Minimum 120px per kolom

    def get_content_height(self):
        """Hitung tinggi konten tabel"""
        if not self.entries:
            return self.rows * 30  # Default tinggi per baris
        
        # Hitung tinggi berdasarkan jumlah baris
        row_height = 30  # Tinggi per baris
        total_height = self.rows * row_height
        
        return max(total_height, self.rows * 30)  # Minimum 30px per baris

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
    def __init__(self, parent, bg_color="#2c3e50", fg_color="white", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=bg_color)
        
        self.time_label = tk.Label(
            self,
            text="",
            relief="flat",
            anchor="e",
            font=("Courier", 10),
            bg=bg_color,
            fg=fg_color,
            padx=15,
            pady=8
        )
        self.time_label.pack(side="bottom", fill="x")
        self.update_time()

    def update_time(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("  %H:%M:%S | %d-%m-%Y"))
        self.after(1000, self.update_time)