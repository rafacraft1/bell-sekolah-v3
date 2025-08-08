# gui/splash_screen.py
import tkinter as tk
from tkinter import ttk
import time
from PIL import Image, ImageTk
import os
from constants import ASSETS_DIR, VERSION
from utils import resource_path

class SplashScreen:
    def __init__(self, callback):
        self.callback = callback
        self.root = tk.Tk()
        self.root.title("Bell Sekolah Otomatis - Loading")
        
        # Hilangkan border dan taskbar
        self.root.overrideredirect(True)
        
        # Posisikan di tengah layar
        window_width = 500
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Set background
        self.root.configure(bg="#2c3e50")
        
        # Buat frame utama
        self.main_frame = tk.Frame(self.root, bg="#2c3e50")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo
        self.logo_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.logo_frame.pack(pady=10)
        
        try:
            # Gunakan logo.ico
            logo_path = resource_path(os.path.join(ASSETS_DIR, "logo.ico"))
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((80, 80), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(self.logo_frame, image=self.logo_photo, bg="#2c3e50")
                logo_label.pack()
        except Exception as e:
            # Fallback jika logo tidak ditemukan
            logo_label = tk.Label(self.logo_frame, text="🔔", font=("Arial", 48), bg="#2c3e50", fg="white")
            logo_label.pack()
        
        # Judul dan versi
        title_label = tk.Label(
            self.main_frame,
            text="Bell Sekolah Otomatis",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=(10, 5))
        
        version_label = tk.Label(
            self.main_frame,
            text=f"Version {VERSION}",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        version_label.pack()
        
        # Frame untuk progress
        self.progress_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.progress_frame.pack(fill=tk.X, pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Memulai aplikasi...")
        self.status_label = tk.Label(
            self.progress_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            bg="#2c3e50",
            fg="white",
            wraplength=400
        )
        self.status_label.pack()
        
        # Copyright
        copyright_label = tk.Label(
            self.main_frame,
            text="© 2025 Bell Sekolah Otomatis. All rights reserved.",
            font=("Arial", 8),
            bg="#2c3e50",
            fg="#95a5a6"
        )
        copyright_label.pack(side=tk.BOTTOM, pady=10)
        
        # Inisialisasi status
        self.steps = [
            "Membuat folder aplikasi...",
            "Menginisialisasi database...",
            "Memeriksa database...",
            "Memuat data default...",
            "Mempersiapkan antarmuka...",
            "Memuat file audio...",
            "Memuat jadwal...",
            "Menginisialisasi pemutar audio...",
            "Mengatur sistem tray...",
            "Menyelesaikan inisialisasi..."
        ]
        
        self.current_step = 0
        self.total_steps = len(self.steps)
        
        # Mulai proses setelah splash screen tampil
        self.root.after(100, self.start_initialization)
    
    def start_initialization(self):
        """Mulai proses inisialisasi"""
        self.update_status()
    
    def update_status(self):
        """Update progress bar dan status text"""
        if self.current_step < self.total_steps:
            # Update status text
            self.status_var.set(self.steps[self.current_step])
            
            # Update progress bar
            progress_value = (self.current_step + 1) * 100 / self.total_steps
            self.progress_var.set(progress_value)
            
            # Increment step
            self.current_step += 1
            
            # Schedule next update
            self.root.after(500, self.update_status)  # 500ms per step
        else:
            # Semua langkah selesai, tunggu 2 detik tambahan
            self.status_var.set("Inisialisasi selesai. Memulai aplikasi...")
            self.root.after(2000, self.close)
    
    def close(self):
        """Tutup splash screen dan jalankan callback"""
        self.root.destroy()
        if self.callback:
            self.callback()
    
    def run(self):
        """Jalankan splash screen"""
        self.root.mainloop()