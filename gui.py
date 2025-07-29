# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os
import sys
import shutil
import threading
import math
import pygame
from PIL import Image, ImageTk, ImageDraw
import pystray
from pystray import MenuItem as item
from data_manager import add_schedule, delete_day, get_schedules, delete_schedule, reset_to_default
from logger import log_error
from config import __version__
from scheduler import BellScheduler

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


class SchoolBellApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bell Sekolah Otomatis")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.audio_path = tk.StringVar()         # Path lengkap (internal)
        self.path_display_var = tk.StringVar()   # Hanya nama file (tampilan)
        self._setup_ui()
        self.scheduler = None
        self.start_scheduler()
        self.setup_tray()

    def _setup_ui(self):
        # Header
        tk.Label(self.root, text="Bell Sekolah Otomatis", font=("Arial", 16, "bold")).pack(pady=10)

        # Input Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Hari:").grid(row=0, column=0, padx=5)
        self.day_var = tk.StringVar(value="Senin")
        day_cb = ttk.Combobox(input_frame, textvariable=self.day_var,
                              values=["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"], state="readonly", width=10)
        day_cb.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Jam:").grid(row=0, column=2, padx=5)
        self.time_var = tk.StringVar(value="06:10")
        tk.Entry(input_frame, textvariable=self.time_var, width=8).grid(row=0, column=3, padx=5)

        # Label Pilih dari Daftar
        tk.Label(input_frame, text="Pilih dari Daftar:").grid(row=0, column=4, padx=5)

        # Combobox untuk file MP3 di folder audio/
        self.mp3_combobox = ttk.Combobox(input_frame, width=30, state="readonly")
        self.mp3_combobox.grid(row=0, column=5, padx=5)

        # Tombol Upload Audio
        tk.Button(input_frame, text="📁 Upload Audio", command=self.upload_audio).grid(row=0, column=6, padx=5)

        # Tombol Play
        self.play_button = tk.Button(input_frame, text="▶ Play", command=self.play_audio, state="disabled")
        self.play_button.grid(row=0, column=7, padx=5)

        # Tambah
        tk.Button(input_frame, text="Tambah", command=self.add_schedule).grid(row=0, column=8, padx=5)

        # 🔁 load_audio_files() dipanggil SETELAH play_button didefinisikan
        self.load_audio_files()

        # Analog Clock - Pindahkan ke pojok kiri atas, tidak tumpang tindih
        clock_frame = tk.Frame(self.root)
        clock_frame.place(x=10, y=10)  # Atur posisi manual
        self.clock = ClockFace(clock_frame)
        self.clock.pack()

        # Table Frame - Tabel dengan header hari
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
        for col, day in enumerate(days):
            tk.Label(table_frame, text=day, relief="groove", width=15, bg="lightgray", font=("Arial", 10, "bold")).grid(row=0, column=col, sticky="nsew")

        # Grid jadwal (10 baris)
        self.schedule_entries = []
        for row in range(10):
            row_entries = []
            for col in range(6):
                entry = tk.Entry(table_frame, width=15, relief="groove", bg="lightgreen")
                entry.grid(row=row+1, column=col, sticky="nsew")
                row_entries.append(entry)
            self.schedule_entries.append(row_entries)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Hapus Jadwal Hari Ini", command=self.clear_day).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Muat Ulang", command=self.load_schedule).pack(side="left", padx=5)

        # Status Bar - Hanya Jam & Tanggal (Kolom 3)
        self.time_label = tk.Label(
            self.root,
            text="",
            relief="sunken",
            anchor="e",
            font=("Courier", 9),
            bg="lightgray",
            fg="black"
        )
        self.time_label.pack(side="bottom", fill="x", padx=1, pady=1)

        # Inisialisasi waktu
        self.update_time()
        self.load_schedule()

    def update_time(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("  %H:%M:%S | %d-%m-%Y"))
        self.root.after(1000, self.update_time)

    def load_audio_files(self):
        """Muat daftar file MP3 dari folder audio/ ke combobox"""
        audio_dir = "audio"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        mp3_files = [f for f in os.listdir(audio_dir) if f.lower().endswith(".mp3")]
        mp3_files.sort()
        self.mp3_combobox['values'] = mp3_files
        if mp3_files:
            self.mp3_combobox.current(0)
            selected_file = mp3_files[0]
            full_path = os.path.join(audio_dir, selected_file)
            self.audio_path.set(full_path)
            self.path_display_var.set(selected_file)
            self.play_button.config(state="normal")
        else:
            self.mp3_combobox.set("")
            self.audio_path.set("")
            self.path_display_var.set("")
            self.play_button.config(state="disabled")

    def on_combobox_select(self, event=None):
        """Saat file dipilih dari combobox"""
        filename = self.mp3_combobox.get()
        if filename:
            full_path = os.path.join("audio", filename)
            self.audio_path.set(full_path)
            self.path_display_var.set(filename)
            self.play_button.config(state="normal")

    def upload_audio(self):
        """Upload file MP3 dari luar ke folder audio/"""
        path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if not path:
            return
        filename = os.path.basename(path)
        dest_path = os.path.join("audio", filename)
        try:
            os.makedirs("audio", exist_ok=True)
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
            log_error(f"Gagal upload file {path}: {e}")
            messagebox.showerror("Error", f"Gagal upload file:\n{str(e)}")

    def play_audio(self):
        """Putar file audio yang dipilih"""
        path = self.audio_path.get()
        if not path:
            messagebox.showwarning("Peringatan", "Belum ada file MP3 yang dipilih.")
            return
        if not os.path.exists(path):
            messagebox.showerror("Error", f"File tidak ditemukan:\n{path}")
            return
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                self.root.update()
                import time
                time.sleep(0.1)
            pygame.mixer.quit()
        except Exception as e:
            log_error(f"Gagal memutar audio {path}: {e}")
            messagebox.showerror("Error", f"Gagal memutar audio:\n{str(e)}")

    def add_schedule(self):
        day = self.day_var.get()
        time = self.time_var.get()
        path = self.audio_path.get()
        if not path or not time:
            messagebox.showwarning("Peringatan", "Isi waktu dan pilih file MP3.")
            return
        try:
            datetime.strptime(time, "%H:%M")
            add_schedule(day, time, path)
            self.load_schedule()
        except ValueError:
            messagebox.showerror("Error", "Format waktu salah. Gunakan HH:MM")

    def load_schedule(self):
        for row in self.schedule_entries:
            for entry in row:
                entry.delete(0, tk.END)
        schedules = get_schedules()
        day_map = {"Senin": 0, "Selasa": 1, "Rabu": 2, "Kamis": 3, "Jumat": 4, "Sabtu": 5}
        for day, day_idx in day_map.items():
            day_schedules = schedules.get(day, [])
            for row_idx, (time, path) in enumerate(day_schedules):
                if row_idx < 10:
                    filename = os.path.basename(path)
                    self.schedule_entries[row_idx][day_idx].insert(0, f"{time} - {filename}")

    def clear_day(self):
        day = self.day_var.get()
        confirm = messagebox.askyesno("Konfirmasi", f"Hapus semua jadwal {day}?")
        if confirm:
            delete_day(day)
            self.load_schedule()

    def start_scheduler(self):
        try:
            self.scheduler = BellScheduler()
        except Exception as e:
            log_error(f"Scheduler gagal: {e}")
            messagebox.showerror("Error", "Gagal memulai scheduler.")

    def on_close(self):
        """Minimize ke tray saat tombol close diklik"""
        self.root.withdraw()

    def setup_tray(self):
        image_path = self.resource_path("assets/bell.png")
        if os.path.exists(image_path):
            image = Image.open(image_path)
        else:
            image = Image.new('RGB', (64, 64), 'orange')
            d = ImageDraw.Draw(image)
            d.text((10, 25), "BELL", fill="white")
        menu = (
            item('Buka Aplikasi', self.show_window),
            item('Lihat Jadwal Hari Ini', self.show_schedule),
            item('Reset ke Default', self.reset_to_default),
            item('Autostart: On', lambda: self.toggle_autostart(True)),
            item('Keluar', self.quit_app)
        )
        self.tray_icon = pystray.Icon("bell", image, "Bell Sekolah", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon, item):
        self.root.deiconify()

    def show_schedule(self, icon, item):
        day_map = {"Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
                   "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu"}
        today = day_map.get(datetime.now().strftime("%A"), "Senin")
        schedules = get_schedules().get(today, [])
        msg = "\n".join([f"{t} - {os.path.basename(p)}" for t, p in schedules])
        if not msg:
            msg = "Tidak ada jadwal hari ini."
        messagebox.showinfo(f"Jadwal {today}", msg)

    def reset_to_default(self, icon, item):
        confirm = messagebox.askyesno("Reset", "Yakin ingin reset ke konfigurasi default?")
        if confirm:
            reset_to_default()
            self.load_schedule()
            messagebox.showinfo("Reset", "Aplikasi telah direset ke konfigurasi default.")

    def toggle_autostart(self, enable=True):
        try:
            import winreg as reg
            key = reg.HKEY_CURRENT_USER
            sub_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            app_name = "SchoolBell"
            exe_path = os.path.abspath(sys.argv[0])
            if enable:
                reg.SetValue(key, sub_key + "\\" + app_name, reg.REG_SZ, exe_path)
                messagebox.showinfo("Autostart", "✅ Akan berjalan saat login.")
            else:
                try:
                    reg.DeleteValue(key, sub_key + "\\" + app_name)
                    messagebox.showinfo("Autostart", "❌ Autostart dinonaktifkan.")
                except:
                    pass
        except Exception as e:
            log_error(f"Autostart gagal: {e}")
            messagebox.showerror("Error", "Gagal mengatur autostart.")

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        if self.scheduler:
            self.scheduler.stop()
        self.root.quit()
        self.root.destroy()

    def resource_path(self, relative_path):
        """Dapatkan path absolut, bekerja untuk dev dan PyInstaller."""
        try:
            base = sys._MEIPASS
        except Exception:
            base = os.path.abspath(".")
        return os.path.join(base, relative_path)


def main():
    from data_manager import init_db, is_database_empty, insert_dummy_data
    init_db()
    os.makedirs("audio", exist_ok=True)
    if is_database_empty():
        insert_dummy_data()
    root = tk.Tk()
    app = SchoolBellApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()