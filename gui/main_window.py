# gui/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
from datetime import datetime
from data_manager import data_manager
from audio_player import AudioPlayer
from logger import log_error, log_info
from constants import AUDIO_DIR, AUDIO_FORMATS, DAYS, ASSETS_DIR, BELL_ICON
from utils import resource_path
from .components import ClockFace, ScheduleTable, StatusBar

class SchoolBellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bell Sekolah Otomatis")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Variables
        self.audio_path = tk.StringVar()         # Path lengkap (internal)
        self.path_display_var = tk.StringVar()   # Hanya nama file (tampilan)
        
        # Audio player
        self.audio_player = AudioPlayer()
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self.load_audio_files()
        self.load_schedule()
        
        # Setup close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_ui(self):
        # Header
        tk.Label(self.root, text="Bell Sekolah Otomatis", font=("Arial", 16, "bold")).pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Hari:").grid(row=0, column=0, padx=5)
        self.day_var = tk.StringVar(value="Senin")
        day_cb = ttk.Combobox(input_frame, textvariable=self.day_var,
                              values=DAYS, state="readonly", width=10)
        day_cb.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Jam:").grid(row=0, column=2, padx=5)
        self.time_var = tk.StringVar(value="06:10")
        tk.Entry(input_frame, textvariable=self.time_var, width=8).grid(row=0, column=3, padx=5)

        # Label Pilih dari Daftar
        tk.Label(input_frame, text="Pilih dari Daftar:").grid(row=0, column=4, padx=5)

        # Combobox untuk file audio di folder audio/
        self.mp3_combobox = ttk.Combobox(input_frame, width=30, state="readonly")
        self.mp3_combobox.grid(row=0, column=5, padx=5)
        self.mp3_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Tombol Upload Audio
        tk.Button(input_frame, text="📁 Upload Audio", command=self.upload_audio).grid(row=0, column=6, padx=5)

        # Tombol Play
        self.play_button = tk.Button(input_frame, text="▶ Play", command=self.play_audio, state="disabled")
        self.play_button.grid(row=0, column=7, padx=5)

        # Tambah
        tk.Button(input_frame, text="Tambah", command=self.add_schedule).grid(row=0, column=8, padx=5)

        # Analog Clock - Posisi di pojok kiri atas
        clock_frame = tk.Frame(self.root)
        clock_frame.place(x=10, y=10)
        self.clock = ClockFace(clock_frame)
        self.clock.pack()

        # Table Frame - Tabel dengan header hari
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.schedule_table = ScheduleTable(table_frame, rows=10)
        self.schedule_table.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Hapus Jadwal Hari Ini", command=self.clear_day).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Muat Ulang", command=self.load_schedule).pack(side="left", padx=5)

        # Status Bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side="bottom", fill="x")

    def load_audio_files(self):
        """Muat daftar file audio dari folder audio/ ke combobox"""
        try:
            if not os.path.exists(AUDIO_DIR):
                os.makedirs(AUDIO_DIR)
            
            audio_files = []
            for ext in AUDIO_FORMATS:
                audio_files.extend([f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(ext)])
            
            audio_files.sort()
            self.mp3_combobox['values'] = audio_files
            
            if audio_files:
                self.mp3_combobox.current(0)
                selected_file = audio_files[0]
                full_path = os.path.join(AUDIO_DIR, selected_file)
                self.audio_path.set(full_path)
                self.path_display_var.set(selected_file)
                self.play_button.config(state="normal")
            else:
                self.mp3_combobox.set("")
                self.audio_path.set("")
                self.path_display_var.set("")
                self.play_button.config(state="disabled")
        except Exception as e:
            log_error(f"Gagal load audio files: {e}")
            messagebox.showerror("Error", f"Gagal memuat file audio:\n{str(e)}")

    def on_combobox_select(self, event=None):
        """Saat file dipilih dari combobox"""
        try:
            filename = self.mp3_combobox.get()
            if filename:
                full_path = os.path.join(AUDIO_DIR, filename)
                self.audio_path.set(full_path)
                self.path_display_var.set(filename)
                self.play_button.config(state="normal")
        except Exception as e:
            log_error(f"Gagal pilih file: {e}")
            messagebox.showerror("Error", f"Gagal memilih file:\n{str(e)}")

    def upload_audio(self):
        """Upload file audio dari luar ke folder audio/"""
        try:
            filetypes = [(f"{ext.upper()} files", f"*{ext}") for ext in AUDIO_FORMATS]
            path = filedialog.askopenfilename(filetypes=filetypes)
            if not path:
                return
            
            filename = os.path.basename(path)
            dest_path = os.path.join(AUDIO_DIR, filename)
            
            os.makedirs(AUDIO_DIR, exist_ok=True)
            if os.path.exists(dest_path):
                if not messagebox.askyesno("Timpa?", f"File '{filename}' sudah ada. Timpa?"):
                    return
            
            shutil.copy2(path, dest_path)
            messagebox.showinfo("Sukses", f"File berhasil di-upload ke folder 'audio'.")
            self.load_audio_files()  # Refresh combobox
            
            # Pilih file yang baru di-upload
            idx = self.mp3_combobox['values'].index(filename)
            self.mp3_combobox.current(idx)
            self.on_combobox_select()
        except Exception as e:
            log_error(f"Gagal upload file: {e}")
            messagebox.showerror("Error", f"Gagal upload file:\n{str(e)}")

    def play_audio(self):
        """Putar file audio yang dipilih"""
        try:
            path = self.audio_path.get()
            if not path:
                messagebox.showwarning("Peringatan", "Belum ada file audio yang dipilih.")
                return
            
            if not os.path.exists(path):
                messagebox.showerror("Error", f"File tidak ditemukan:\n{path}")
                return
            
            # Nonaktifkan tombol play sementara
            self.play_button.config(state="disabled", text="⏸ Playing...")
            self.root.update()  # Force update UI
            
            # Putar audio di thread terpisah agar UI tidak freeze
            threading.Thread(
                target=self._play_audio_thread,
                args=(path,),
                daemon=True
            ).start()
        except Exception as e:
            log_error(f"Gagal putar audio: {e}")
            messagebox.showerror("Error", f"Gagal memutar audio:\n{str(e)}")
            self.play_button.config(state="normal", text="▶ Play")

    def _play_audio_thread(self, path):
        """Putar audio di thread terpisah"""
        try:
            if self.audio_player.play_audio(path, blocking=True):
                # Berhasil diputar
                pass
            else:
                # Gagal diputar
                self.root.after(0, lambda: messagebox.showerror("Error", "Gagal memutar audio"))
        except Exception as e:
            log_error(f"Error di thread audio: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Gagal memutar audio:\n{str(e)}"))
        finally:
            # Aktifkan kembali tombol play
            self.root.after(0, lambda: self.play_button.config(state="normal", text="▶ Play"))

    def add_schedule(self):
        """Tambah jadwal baru"""
        try:
            day = self.day_var.get()
            schedule_time = self.time_var.get()
            path = self.audio_path.get()
            
            if not path or not schedule_time:
                messagebox.showwarning("Peringatan", "Isi waktu dan pilih file audio.")
                return
            
            # Validasi format waktu
            try:
                datetime.strptime(schedule_time, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Format waktu salah. Gunakan HH:MM")
                return
            
            if data_manager.add_schedule(day, schedule_time, path):
                # Refresh schedule table immediately
                self.load_schedule(force_refresh=True)
                messagebox.showinfo("Sukses", "Jadwal berhasil ditambahkan.")
            else:
                messagebox.showerror("Error", "Gagal menambahkan jadwal.")
        except Exception as e:
            log_error(f"Gagal tambah jadwal: {e}")
            messagebox.showerror("Error", f"Gagal menambahkan jadwal:\n{str(e)}")

    def load_schedule(self, force_refresh=False):
        """Load schedule from database"""
        try:
            # Force refresh data from database
            schedules = data_manager.get_schedules(force_refresh=force_refresh)
            self.schedule_table.update_schedule(schedules)
        except Exception as e:
            log_error(f"Gagal load jadwal: {e}")
            messagebox.showerror("Error", f"Gagal memuat jadwal:\n{str(e)}")

    def clear_day(self):
        """Hapus semua jadwal hari tertentu"""
        try:
            day = self.day_var.get()
            confirm = messagebox.askyesno("Konfirmasi", f"Hapus semua jadwal {day}?")
            if confirm:
                if data_manager.delete_day(day):
                    # Refresh schedule table immediately
                    self.load_schedule(force_refresh=True)
                    messagebox.showinfo("Sukses", f"Jadwal hari {day} berhasil dihapus.")
                else:
                    messagebox.showerror("Error", f"Gagal menghapus jadwal hari {day}.")
        except Exception as e:
            log_error(f"Gagal hapus jadwal hari: {e}")
            messagebox.showerror("Error", f"Gagal menghapus jadwal:\n{str(e)}")

    def on_close(self):
        """Minimize ke tray saat tombol close diklik"""
        try:
            self.root.withdraw()
        except Exception as e:
            log_error(f"Gagal minimize ke tray: {e}")

    def quit_app(self):
        """Quit application"""
        try:
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            log_error(f"Gagal keluar aplikasi: {e}")