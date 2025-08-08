# gui/splash_screen.py
import tkinter as tk
from tkinter import ttk
import time
from PIL import Image, ImageTk
import os
from constants import ASSETS_DIR, VERSION
from utils import resource_path

class SplashScreen:
    def __init__(self):
        print("Creating splash screen...")  # Debug print
        
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
                print("Logo loaded successfully")  # Debug print
        except Exception as e:
            # Fallback jika logo tidak ditemukan
            logo_label = tk.Label(self.logo_frame, text="🔔", font=("Arial", 48), bg="#2c3e50", fg="white")
            logo_label.pack()
            print(f"Failed to load logo: {e}")  # Debug print
        
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
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        print("Progress bar created")  # Debug print
        
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
        
        # Progress percentage label
        self.progress_percent_var = tk.StringVar(value="0%")
        self.progress_percent_label = tk.Label(
            self.progress_frame,
            textvariable=self.progress_percent_var,
            font=("Arial", 9),
            bg="#2c3e50",
            fg="white"
        )
        self.progress_percent_label.pack()
        
        # Copyright
        copyright_label = tk.Label(
            self.main_frame,
            text="© 2025 Bell Sekolah Otomatis. All rights reserved.",
            font=("Arial", 8),
            bg="#2c3e50",
            fg="#95a5a6"
        )
        copyright_label.pack(side=tk.BOTTOM, pady=10)
        
        # Force update UI
        self.root.update()
        print("Splash screen initialized successfully")  # Debug print
    
    def update_progress(self, message=None, progress=None):
        """Update progress bar dan status text"""
        try:
            print(f"Updating progress: {message} - {progress}%")  # Debug print
            
            # Update status text
            if message:
                self.status_var.set(message)
            
            # Update progress bar
            if progress is not None:
                self.progress_var.set(progress)
                self.progress_percent_var.set(f"{progress}%")
            
            # Force update UI
            self.root.update()
            print(f"Progress updated successfully: {message} - {progress}%")  # Debug print
                
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def close(self):
        """Tutup splash screen"""
        try:
            print("Closing splash screen")  # Debug print
            self.root.destroy()
        except Exception as e:
            print(f"Error closing splash screen: {e}")
    
    def run(self):
        """Jalankan splash screen"""
        print("Starting splash screen mainloop")  # Debug print
        self.root.mainloop()