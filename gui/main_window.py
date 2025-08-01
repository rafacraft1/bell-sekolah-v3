# gui/main_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
from datetime import datetime
import math
import sys
import pygame
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
        self.root.geometry("1000x650")  # Ukuran fix
        self.root.resizable(False, False)  # Tidak bisa di-resize
        
        # Set window icon
        self._set_window_icon()
        
        # Set theme colors
        self.bg_color = "#f5f6fa"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#f39c12"
        self.danger_color = "#e74c3c"
        self.info_color = "#9b59b6"
        self.text_color = "#2c3e50"
        self.white_color = "#ffffff"
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.audio_path = tk.StringVar()
        self.path_display_var = tk.StringVar()
        
        # Audio player
        self.audio_player = AudioPlayer()
        
        # Setup UI
        self._setup_ui()
        
        # Load initial data
        self.load_audio_files()
        self.load_schedule()
        
        # Setup close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _set_window_icon(self):
        """Set icon untuk window aplikasi dengan multiple fallback"""
        try:
            # Debug: Cetak informasi icon
            print("Setting window icon...")
            
            # Dapatkan path icon dengan beberapa metode
            icon_paths = []
            
            # Metode 1: Gunakan resource_path
            icon_path1 = resource_path(os.path.join(ASSETS_DIR, BELL_ICON))
            icon_paths.append(("resource_path", icon_path1))
            
            # Metode 2: Gunakan absolute path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path2 = os.path.join(base_dir, "..", "assets", BELL_ICON)
            icon_path2 = os.path.abspath(icon_path2)
            icon_paths.append(("absolute_path", icon_path2))
            
            # Metode 3: Coba di direktori kerja
            icon_path3 = os.path.join("assets", BELL_ICON)
            icon_paths.append(("working_dir", icon_path3))
            
            # Coba semua path
            icon_set = False
            for method, path in icon_paths:
                print(f"Trying {method}: {path}")
                print(f"File exists: {os.path.exists(path)}")
                
                if os.path.exists(path):
                    try:
                        # Untuk Windows, coba iconbitmap
                        if sys.platform == "win32" and path.lower().endswith('.ico'):
                            self.root.iconbitmap(path)
                            print(f"Icon set using iconbitmap from {method}")
                            icon_set = True
                            break
                        else:
                            # Untuk cross-platform atau file non-ICO
                            from PIL import Image, ImageTk
                            icon_img = Image.open(path)
                            icon_photo = ImageTk.PhotoImage(icon_img)
                            self.root.iconphoto(True, icon_photo)
                            print(f"Icon set using iconphoto from {method}")
                            icon_set = True
                            break
                    except Exception as e:
                        print(f"Failed to set icon from {method}: {e}")
                        continue
            
            # Jika semua metode gagal, buat icon default
            if not icon_set:
                print("All icon methods failed, creating default icon")
                self._create_default_icon()
                
        except Exception as e:
            log_error(f"Gagal mengatur window icon: {e}")
            print(f"Error in _set_window_icon: {e}")
            self._create_default_icon()

    def _create_default_icon(self):
        """Buat icon default menggunakan Tkinter"""
        try:
            print("Creating default icon...")
            
            # Buat PhotoImage sederhana sebagai icon
            icon_img = tk.PhotoImage(width=32, height=32)
            
            # Gambar bentuk lonceng sederhana
            # Background transparan
            for x in range(32):
                for y in range(32):
                    icon_img.put("#FFFFFF00", (x, y))  # Transparan
            
            # Gambar badan lonceng (lingkaran)
            center_x, center_y = 16, 16
            radius = 8
            for x in range(32):
                for y in range(32):
                    if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        icon_img.put("#FFD700", (x, y))  # Emas
            
            # Gambar gagang lonceng
            for x in range(14, 18):
                for y in range(6, 10):
                    icon_img.put("#8B4513", (x, y))  # Coklat
            
            # Atur sebagai icon
            self.root.iconphoto(True, icon_img)
            print("Default icon created successfully")
            
        except Exception as e:
            log_error(f"Gagal membuat default icon: {e}")
            print(f"Error creating default icon: {e}")

    def _setup_ui(self):
        # Header with gradient effect
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Logo and title
        logo_frame = tk.Frame(header_frame, bg=self.primary_color)
        logo_frame.pack(side="left", padx=20, pady=10)
        
        # Add bell icon if available
        try:
            bell_icon_path = resource_path(os.path.join(ASSETS_DIR, BELL_ICON))
            if os.path.exists(bell_icon_path):
                from PIL import Image, ImageTk
                bell_img = Image.open(bell_icon_path)
                bell_img = bell_img.resize((40, 40), Image.LANCZOS)
                bell_photo = ImageTk.PhotoImage(bell_img)
                bell_label = tk.Label(logo_frame, image=bell_photo, bg=self.primary_color)
                bell_label.image = bell_photo
                bell_label.pack(side="left", padx=(0, 10))
        except:
            pass
        
        title_label = tk.Label(
            logo_frame, 
            text="Bell Sekolah Otomatis", 
            font=("Arial", 20, "bold"),
            bg=self.primary_color,
            fg=self.white_color
        )
        title_label.pack(side="left", pady=15)
        
        # Version label
        version_label = tk.Label(
            header_frame,
            text="v2.0.0",
            font=("Arial", 10),
            bg=self.primary_color,
            fg="#ecf0f1"
        )
        version_label.pack(side="right", padx=20, pady=15)

        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Top section - Input and Clock side by side
        top_section = tk.Frame(main_container, bg=self.bg_color)
        top_section.pack(fill="x", pady=(0, 15))
        
        # Left panel - Input section with card design
        input_card = tk.Frame(top_section, bg=self.white_color, relief="flat", bd=0)
        input_card.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Card header
        card_header = tk.Frame(input_card, bg=self.primary_color, height=40)
        card_header.pack(fill="x")
        card_header.pack_propagate(False)
        
        tk.Label(
            card_header,
            text="Pengaturan Jadwal",
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg=self.white_color,
            padx=15,
            pady=8
        ).pack(side="left")
        
        # Card content
        card_content = tk.Frame(input_card, bg=self.white_color, padx=20, pady=15)
        card_content.pack(fill="x")
        
        # Input fields in two rows
        # Row 1
        row1 = tk.Frame(card_content, bg=self.white_color)
        row1.pack(fill="x", pady=(0, 10))
        
        tk.Label(row1, text="Hari:", font=("Arial", 10), bg=self.white_color, fg=self.text_color).grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        self.day_var = tk.StringVar(value="Senin")
        day_cb = ttk.Combobox(row1, textvariable=self.day_var, values=DAYS, state="readonly", width=12, font=("Arial", 10))
        day_cb.grid(row=0, column=1, padx=(0, 20))
        
        tk.Label(row1, text="Jam:", font=("Arial", 10), bg=self.white_color, fg=self.text_color).grid(row=0, column=2, sticky="w", padx=(0, 5))
        
        self.time_var = tk.StringVar(value="06:10")
        time_entry = tk.Entry(row1, textvariable=self.time_var, width=10, font=("Arial", 10))
        time_entry.grid(row=0, column=3, padx=(0, 20))
        
        tk.Label(row1, text="Audio:", font=("Arial", 10), bg=self.white_color, fg=self.text_color).grid(row=0, column=4, sticky="w", padx=(0, 5))
        
        self.mp3_combobox = ttk.Combobox(row1, width=35, state="readonly", font=("Arial", 10))
        self.mp3_combobox.grid(row=0, column=5, padx=(0, 10))
        self.mp3_combobox.bind("<<ComboboxSelected>>", self.on_combobox_select)
        
        # Row 2 - Buttons
        row2 = tk.Frame(card_content, bg=self.white_color)
        row2.pack(fill="x")
        
        # Create styled buttons
        self.upload_btn = self._create_styled_button(
            row2, "📁 Upload Audio", self.secondary_color, self.upload_audio
        )
        self.upload_btn.pack(side="left", padx=(0, 10))
        
        self.play_button = self._create_styled_button(
            row2, "▶ Play", self.success_color, self.play_audio, state="disabled"
        )
        self.play_button.pack(side="left", padx=(0, 10))
        
        self.add_btn = self._create_styled_button(
            row2, "Tambah Jadwal", self.danger_color, self.add_schedule
        )
        self.add_btn.pack(side="left")
        
        # Right panel - Clock (no background card)
        clock_frame = tk.Frame(top_section, bg=self.bg_color, width=180, height=180)
        clock_frame.pack(side="right", fill="none")
        clock_frame.pack_propagate(False)
        
        # Clock centered in frame
        self.clock = ClockFace(clock_frame)
        self.clock.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bottom section - Schedule table
        schedule_section = tk.Frame(main_container, bg=self.white_color)
        schedule_section.pack(fill="both", expand=True)
        
        # Table header
        table_header = tk.Frame(schedule_section, bg=self.primary_color, height=40)
        table_header.pack(fill="x")
        table_header.pack_propagate(False)
        
        # Konfigurasi grid header agar responsive
        for col in range(len(DAYS)):
            table_header.grid_columnconfigure(col, weight=1, uniform="header_cols")
        
        for col, day in enumerate(DAYS):
            day_label = tk.Label(
                table_header,
                text=day,
                font=("Arial", 11, "bold"),
                bg=self.primary_color,
                fg=self.white_color,
                width=15,
                relief="flat"
            )
            day_label.grid(row=0, column=col, sticky="nsew", padx=1)
        
        # Simpan referensi ke header labels untuk update responsivitas
        self.header_labels = []
        for col, day in enumerate(DAYS):
            for widget in table_header.grid_slaves(row=0, column=col):
                if isinstance(widget, tk.Label):
                    self.header_labels.append(widget)
        
        # Create scrollable frame for schedule table
        scrollable_frame = tk.Frame(schedule_section, bg="white")
        scrollable_frame.pack(fill="both", expand=True)
        scrollable_frame.grid_rowconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_rowconfigure(1, weight=0)  # Row untuk horizontal scrollbar
        scrollable_frame.grid_columnconfigure(1, weight=0)  # Column untuk vertical scrollbar
        
        # Create canvas and scrollbars
        self.canvas = tk.Canvas(scrollable_frame, highlightthickness=0, bg="white", takefocus=True)
        
        # Scrollbar vertikal dengan grid_remove untuk menyembunyikan
        self.scrollbar_v = tk.Scrollbar(scrollable_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.scrollbar_v.grid_remove()  # Sembunyikan scrollbar awalnya
        
        # Scrollbar horizontal dengan grid_remove untuk menyembunyikan
        self.scrollbar_h = tk.Scrollbar(scrollable_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_h.grid(row=1, column=0, sticky="ew")
        self.scrollbar_h.grid_remove()  # Sembunyikan scrollbar awalnya
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self._update_vertical_scrollbar, 
                             xscrollcommand=self._update_horizontal_scrollbar)
        
        # Pack canvas
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Create frame inside canvas for schedule table
        self.table_container = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.table_container, anchor="nw")
        
        # Schedule table
        self.schedule_table = ScheduleTable(self.table_container, rows=10)
        self.schedule_table.pack(fill="both", expand=True)
        
        # Bind events for scrolling
        self.table_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))   # Linux
        
        # Enable canvas to receive focus for keyboard navigation
        self.canvas.focus_set()
        
        # Status bar
        self.status_bar = StatusBar(self.root, self.primary_color, self.white_color)
        self.status_bar.pack(side="bottom", fill="x")
        
        # Setup keyboard navigation untuk scrolling
        self._setup_keyboard_navigation()

    def _create_styled_button(self, parent, text, color, command, state="normal"):
        """Create a styled button with hover effect"""
        btn = tk.Button(
            parent,
            text=text,
            bg=color,
            fg=self.white_color,
            font=("Arial", 10, "bold"),
            relief="flat",
            bd=0,
            padx=15,
            pady=6,
            cursor="hand2",
            state=state,
            command=command
        )
        
        # Add hover effect
        def on_enter(e):
            btn.config(bg=self._darken_color(color))
            
        def on_leave(e):
            btn.config(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _darken_color(self, color):
        """Darken a hex color by 20%"""
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Darken by 20%
        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

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
            # Cek scrollbar setelah update
            self.root.after(100, self._check_scrollbars)
        except Exception as e:
            log_error(f"Gagal load jadwal: {e}")
            messagebox.showerror("Error", f"Gagal memuat jadwal:\n{str(e)}")

    def on_close(self):
        """Minimize ke tray saat tombol close diklik"""
        try:
            self.root.withdraw()
        except Exception as e:
            log_error(f"Gagal minimize ke tray: {e}")

    def quit_app(self):
        """Quit application dengan benar"""
        try:
            # Hentikan semua proses background
            if hasattr(self, 'audio_player'):
                # Hentikan audio yang sedang diputar
                if self.audio_player.currently_playing:
                    if pygame.mixer.get_init():
                        pygame.mixer.quit()
            
            # Hancurkan window
            self.root.quit()
            self.root.destroy()
            
            # Keluar dari aplikasi
            sys.exit(0)
        except Exception as e:
            log_error(f"Gagal keluar aplikasi: {e}")
            sys.exit(1)

    def _on_frame_configure(self, event):
        """Update scrollregion saat frame berubah ukuran"""
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Update responsivitas
            self._update_table_responsiveness()
            # Cek scrollbar
            self._check_scrollbars()
        except Exception as e:
            log_error(f"Gagal frame configure: {e}")

    def _on_canvas_configure(self, event):
        """Update canvas window size saat canvas berubah ukuran"""
        try:
            # Update lebar canvas window agar sesuai dengan canvas
            if hasattr(self, 'schedule_table'):
                content_width = self.schedule_table.get_content_width()
                self.canvas.itemconfig(self.canvas_window, 
                                     width=max(content_width, event.width))
            # Cek scrollbar
            self._check_scrollbars()
        except Exception as e:
            log_error(f"Gagal canvas configure: {e}")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        try:
            # Scroll vertical
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception as e:
            log_error(f"Gagal mouse wheel: {e}")

    def _on_key_press(self, event):
        """Handle key press events untuk scrolling"""
        try:
            if event.keysym == 'Up':
                self.canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                self.canvas.yview_scroll(1, "units")
            elif event.keysym == 'Left':
                self.canvas.xview_scroll(-1, "units")
            elif event.keysym == 'Right':
                self.canvas.xview_scroll(1, "units")
            elif event.keysym == 'Page_Up':
                self.canvas.yview_scroll(-1, "pages")
            elif event.keysym == 'Page_Down':
                self.canvas.yview_scroll(1, "pages")
            elif event.keysym == 'Home':
                self.canvas.yview_moveto(0)
            elif event.keysym == 'End':
                self.canvas.yview_moveto(1)
        except Exception as e:
            log_error(f"Gagal key press: {e}")

    def _setup_keyboard_navigation(self):
        """Setup keyboard navigation untuk scrolling"""
        self.root.bind("<Up>", lambda e: self._on_key_press(e))
        self.root.bind("<Down>", lambda e: self._on_key_press(e))
        self.root.bind("<Left>", lambda e: self._on_key_press(e))
        self.root.bind("<Right>", lambda e: self._on_key_press(e))
        self.root.bind("<Prior>", lambda e: self._on_key_press(e))  # Page Up
        self.root.bind("<Next>", lambda e: self._on_key_press(e))   # Page Down
        self.root.bind("<Home>", lambda e: self._on_key_press(e))
        self.root.bind("<End>", lambda e: self._on_key_press(e))
        
    def _update_table_responsiveness(self):
        """Update tabel responsivitas berdasarkan ukuran window"""
        try:
            # Dapatkan ukuran canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Valid size
                # Update ukuran font berdasarkan lebar canvas
                base_font_size = max(8, min(12, canvas_width // 100))
                header_font_size = max(9, min(14, base_font_size + 2))
                
                # Update font di header labels
                if hasattr(self, 'header_labels'):
                    for label in self.header_labels:
                        current_font = label.cget("font")
                        if isinstance(current_font, tuple):
                            font_family = current_font[0]
                            new_font = (font_family, header_font_size, "bold")
                        else:
                            new_font = ("Arial", header_font_size, "bold")
                        label.config(font=new_font)
                
                # Update font di schedule table
                if hasattr(self, 'schedule_table'):
                    self.schedule_table.update_font_size(base_font_size)
                
                # Update canvas window size
                if hasattr(self, 'schedule_table'):
                    content_width = self.schedule_table.get_content_width()
                    content_height = self.schedule_table.get_content_height()
                    
                    # Update canvas window size
                    self.canvas.itemconfig(self.canvas_window, 
                                         width=max(content_width, canvas_width),
                                         height=max(content_height, canvas_height))
                    
                    # Update scrollregion
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                                
        except Exception as e:
            log_error(f"Gagal update responsivitas tabel: {e}")

    def _update_vertical_scrollbar(self, first, last):
        """Update vertikal scrollbar dan tampilkan/sembunyikan sesuai kebutuhan"""
        # Update posisi scrollbar
        self.scrollbar_v.set(first, last)
        
        # Cek apakah scrollbar diperlukan
        if self.canvas.bbox("all"):
            canvas_height = self.canvas.winfo_height()
            content_height = self.canvas.bbox("all")[3]
            
            if content_height > canvas_height:
                self.scrollbar_v.grid()  # Tampilkan scrollbar
            else:
                self.scrollbar_v.grid_remove()  # Sembunyikan scrollbar

    def _update_horizontal_scrollbar(self, first, last):
        """Update horizontal scrollbar dan tampilkan/sembunyikan sesuai kebutuhan"""
        # Update posisi scrollbar
        self.scrollbar_h.set(first, last)
        
        # Cek apakah scrollbar diperlukan
        if self.canvas.bbox("all"):
            canvas_width = self.canvas.winfo_width()
            content_width = self.canvas.bbox("all")[2]
            
            if content_width > canvas_width:
                self.scrollbar_h.grid()  # Tampilkan scrollbar
            else:
                self.scrollbar_h.grid_remove()  # Sembunyikan scrollbar

    def _check_scrollbars(self):
        """Cek dan update status scrollbar"""
        if self.canvas.bbox("all"):
            # Update vertikal scrollbar
            canvas_height = self.canvas.winfo_height()
            content_height = self.canvas.bbox("all")[3]
            
            if content_height > canvas_height:
                self.scrollbar_v.grid()  # Tampilkan scrollbar
            else:
                self.scrollbar_v.grid_remove()  # Sembunyikan scrollbar
            
            # Update horizontal scrollbar
            canvas_width = self.canvas.winfo_width()
            content_width = self.canvas.bbox("all")[2]
            
            if content_width > canvas_width:
                self.scrollbar_h.grid()  # Tampilkan scrollbar
            else:
                self.scrollbar_h.grid_remove()  # Sembunyikan scrollbar


# Perbarui kelas ClockFace
class ClockFace(tk.Canvas):
    def __init__(self, parent, **kwargs):
        # Hapus background dengan mengatur highlightthickness
        kwargs['highlightthickness'] = 0
        super().__init__(parent, **kwargs)
        
        # Atur ukuran jam
        self.width = 180
        self.height = 180
        self.configure(width=self.width, height=self.height)
        
        # Pusat jam
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.radius = min(self.width, self.height) // 2 - 10
        
        # Gambar jam
        self.draw_clock()
        
        # Update setiap detik
        self.update_clock()
    
    def draw_clock(self):
        # Hapus semua yang ada di canvas
        self.delete("all")
        
        # Gambar angka jam
        for i in range(1, 13):
            angle = math.radians(i * 30 - 90)  # 0 derajat di posisi 12 jam
            x = self.center_x + self.radius * 0.8 * math.cos(angle)
            y = self.center_y + self.radius * 0.8 * math.sin(angle)
            self.create_text(x, y, text=str(i), font=('Arial', 12, 'bold'), fill='black')
        
        # Gambar titik tengah
        self.create_oval(self.center_x-5, self.center_y-5, self.center_x+5, self.center_y+5, fill='black')
    
    def update_clock(self):
        now = datetime.now()
        
        # Hitung sudut untuk jarum jam, menit, dan detik
        second_angle = math.radians(now.second * 6 - 90)
        minute_angle = math.radians(now.minute * 6 - 90)
        hour_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
        
        # Hapus jarum lama
        self.delete("hour_hand")
        self.delete("minute_hand")
        self.delete("second_hand")
        
        # Gambar jarum jam
        hour_x = self.center_x + self.radius * 0.5 * math.cos(hour_angle)
        hour_y = self.center_y + self.radius * 0.5 * math.sin(hour_angle)
        self.create_line(self.center_x, self.center_y, hour_x, hour_y, width=6, fill='black', tags="hour_hand")
        
        # Gambar jarum menit
        minute_x = self.center_x + self.radius * 0.7 * math.cos(minute_angle)
        minute_y = self.center_y + self.radius * 0.7 * math.sin(minute_angle)
        self.create_line(self.center_x, self.center_y, minute_x, minute_y, width=4, fill='black', tags="minute_hand")
        
        # Gambar jarum detik
        second_x = self.center_x + self.radius * 0.8 * math.cos(second_angle)
        second_y = self.center_y + self.radius * 0.8 * math.sin(second_angle)
        self.create_line(self.center_x, self.center_y, second_x, second_y, width=2, fill='red', tags="second_hand")
        
        # Update setiap detik
        self.after(1000, self.update_clock)