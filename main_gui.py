"""
C-Merch Kiosk - Modern Dashboard GUI
Clean architecture with separated data and code
Auto-converts SVG to PNG for icon display
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import threading

try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ==================== CONFIGURATION DATA ====================
from config.gui_config import (
    # Colors
    BG_MAIN, BG_WHITE, HEADER_BG, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    BTN_CALIBRATION, BTN_START, BTN_TEST, BTN_RESET, BTN_EDIT,
    
    # Labels
    CONFIG_LABELS, CONFIG_DESCRIPTIONS,
    
    # Paths
    BASE_DIR, LOGO_PATH, ICON_PATH, CONFIG_PATH, SETTINGS_PATH,
    MAIN_APP, CALIBRATION_TOOL, TEST_COMPONENTS,
    ICON_DIR
)


def svg_to_png(svg_path, size=(32, 32)):
    """Convert SVG to PNG using PIL (simple approach for basic SVG)"""
    if not HAS_PIL:
        return None
    
    try:
        # Try cairosvg first (if available)
        try:
            import cairosvg
            from io import BytesIO
            png_data = cairosvg.svg2png(
                url=str(svg_path), 
                output_width=size[0], 
                output_height=size[1]
            )
            img = Image.open(BytesIO(png_data))
            return ImageTk.PhotoImage(img)
        except ImportError:
            # Fallback: Create PNG cache
            cache_dir = ICON_DIR / "cache"
            cache_dir.mkdir(exist_ok=True)
            cache_file = cache_dir / f"{svg_path.stem}_{size[0]}x{size[1]}.png"
            
            # Check if cached PNG exists
            if cache_file.exists():
                img = Image.open(cache_file)
                return ImageTk.PhotoImage(img)
            
            # If no cache and no cairosvg, create placeholder
            img = Image.new('RGBA', size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            # Draw simple circle as placeholder
            draw.ellipse([5, 5, size[0]-5, size[1]-5], fill=(100, 100, 100, 200))
            
            # Cache it
            img.save(cache_file, 'PNG')
            return ImageTk.PhotoImage(img)
            
    except Exception as e:
        print(f"Failed to convert SVG {svg_path}: {e}")
        return None


def load_icon_image(icon_name, size=(32, 32)):
    """Load icon from PNG or SVG"""
    if not HAS_PIL:
        return None
    
    # Try PNG first
    png_path = ICON_DIR / f"{icon_name}.png"
    svg_path = ICON_DIR / f"{icon_name}.svg"
    
    try:
        if png_path.exists():
            img = Image.open(png_path)
            img = img.convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        elif svg_path.exists():
            return svg_to_png(svg_path, size)
    except Exception as e:
        print(f"Failed to load icon {icon_name}: {e}")
    
    return None


class ActionButton(tk.Canvas):
    """Large action button with icon and hover effect"""
    
    def __init__(self, parent, text, color, icon_name=None, command=None, **kwargs):
        super().__init__(parent, bg=BG_MAIN, highlightthickness=0, **kwargs)
        
        self.text = text
        self.color = color
        self.icon_name = icon_name
        self.command = command
        self.is_hovered = False
        self.icon_image = None
        
        # Load icon if available
        if icon_name:
            self.icon_image = load_icon_image(icon_name, size=(40, 40))
        
        self.bind("<Configure>", self._on_resize)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _on_resize(self, event=None):
        self.draw()
    
    def draw(self):
        self.delete("all")
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Button background with hover effect
        color = self._adjust_color(self.color, 0.9) if self.is_hovered else self.color
        
        radius = 8
        self._create_rounded_rect(0, 0, width, height, radius, fill=color, outline="")
        
        # Draw icon
        if self.icon_image:
            icon_y = height // 2 - 25
            self.create_image(width // 2, icon_y, image=self.icon_image)
            text_y = height // 2 + 20
        else:
            text_y = height // 2
        
        # Draw text
        self.create_text(width // 2, text_y, text=self.text,
                        fill="white", anchor=tk.CENTER,
                        font=("Segoe UI", 12, "bold"))
    
    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2,
            x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _adjust_color(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _on_enter(self, e):
        self.is_hovered = True
        self.draw()
        self.config(cursor="hand2")
    
    def _on_leave(self, e):
        self.is_hovered = False
        self.draw()
        self.config(cursor="")
    
    def _on_click(self, e):
        if self.command:
            self.command()


class SmallButton(tk.Canvas):
    """Small button for Reset and Edit"""
    
    def __init__(self, parent, text, color, icon_name=None, command=None, **kwargs):
        super().__init__(parent, bg=BG_MAIN, highlightthickness=0, **kwargs)
        
        self.text = text
        self.color = color
        self.icon_name = icon_name
        self.command = command
        self.is_hovered = False
        self.icon_image = None
        
        # Load icon if available
        if icon_name:
            self.icon_image = load_icon_image(icon_name, size=(18, 18))
        
        self.bind("<Configure>", self._on_resize)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _on_resize(self, event=None):
        self.draw()
    
    def draw(self):
        self.delete("all")
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        color = self._adjust_color(self.color, 0.9) if self.is_hovered else self.color
        
        radius = 6
        self._create_rounded_rect(0, 0, width, height, radius, fill=color, outline="")
        
        # Calculate positions
        if self.icon_image:
            icon_x = 25
            text_x = icon_x + 25
            self.create_image(icon_x, height // 2, image=self.icon_image)
        else:
            text_x = width // 2
        
        # Draw text
        anchor = tk.W if self.icon_image else tk.CENTER
        self.create_text(text_x, height // 2, text=self.text,
                        fill="white", anchor=anchor,
                        font=("Segoe UI", 10, "bold"))
    
    def _create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2,
            x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _adjust_color(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _on_enter(self, e):
        self.is_hovered = True
        self.draw()
        self.config(cursor="hand2")
    
    def _on_leave(self, e):
        self.is_hovered = False
        self.draw()
        self.config(cursor="")
    
    def _on_click(self, e):
        if self.command:
            self.command()


class EditConfigDialog(tk.Toplevel):
    """Dialog for editing configuration"""
    
    def __init__(self, parent, config, on_save):
        super().__init__(parent)
        
        self.config = config.copy()
        self.on_save = on_save
        self.result = None
        
        self.title("Edit Data Konfigurasi")
        self.geometry("600x500")
        self.configure(bg=BG_WHITE)
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.build_ui()
    
    def build_ui(self):
        # Header
        header = tk.Frame(self, bg=BTN_CALIBRATION, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Edit Konfigurasi", 
                font=("Segoe UI", 16, "bold"),
                fg="white", bg=BTN_CALIBRATION).pack(pady=15)
        
        # Content
        content = tk.Frame(self, bg=BG_WHITE)
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Create scrollable frame
        canvas = tk.Canvas(content, bg=BG_WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(content, orient=tk.VERTICAL, command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=BG_WHITE)
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create form fields
        self.entries = {}
        
        row = 0
        for key, label_text in CONFIG_LABELS.items():
            if key not in self.config:
                continue
            
            # Label
            tk.Label(scrollable, text=label_text + ":",
                    font=("Segoe UI", 10),
                    fg=TEXT_PRIMARY, bg=BG_WHITE,
                    anchor=tk.W).grid(row=row, column=0, sticky="w", pady=8)
            
            # Entry
            value = self.config[key]
            
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                cb = tk.Checkbutton(scrollable, variable=var,
                                   bg=BG_WHITE, font=("Segoe UI", 10))
                cb.grid(row=row, column=1, sticky="w", pady=8)
                self.entries[key] = var
            else:
                entry = tk.Entry(scrollable, font=("Segoe UI", 10), width=30)
                entry.insert(0, str(value))
                entry.grid(row=row, column=1, sticky="ew", pady=8)
                self.entries[key] = entry
            
            row += 1
        
        scrollable.grid_columnconfigure(1, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        btn_frame = tk.Frame(self, bg=BG_WHITE)
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        tk.Button(btn_frame, text="Batal", 
                 font=("Segoe UI", 10),
                 bg=BTN_EDIT, fg="white",
                 relief=tk.FLAT, cursor="hand2",
                 padx=20, pady=8,
                 command=self.cancel).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="Simpan", 
                 font=("Segoe UI", 10, "bold"),
                 bg=BTN_START, fg="white",
                 relief=tk.FLAT, cursor="hand2",
                 padx=20, pady=8,
                 command=self.save).pack(side=tk.RIGHT, padx=5)
    
    def save(self):
        # Collect values
        new_config = {}
        for key, widget in self.entries.items():
            if isinstance(widget, tk.BooleanVar):
                new_config[key] = widget.get()
            else:
                value_str = widget.get().strip()
                original_value = self.config[key]
                
                if isinstance(original_value, int):
                    try:
                        new_config[key] = int(value_str)
                    except ValueError:
                        messagebox.showerror("Error", 
                                           f"Nilai untuk '{key}' harus berupa angka bulat!",
                                           parent=self)
                        return
                elif isinstance(original_value, float):
                    try:
                        new_config[key] = float(value_str)
                    except ValueError:
                        messagebox.showerror("Error", 
                                           f"Nilai untuk '{key}' harus berupa angka!",
                                           parent=self)
                        return
                else:
                    new_config[key] = value_str
        
        # Confirm save
        if messagebox.askyesno("Konfirmasi", 
                               "Apakah Anda yakin ingin menyimpan perubahan?\n\n"
                               "Perubahan akan diterapkan saat restart aplikasi.",
                               parent=self):
            self.result = new_config
            self.on_save(new_config)
            self.destroy()
    
    def cancel(self):
        self.destroy()


class ModernDashboard:
    """Main Dashboard Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kiosk Control Center")
        
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        self.root.configure(bg=BG_MAIN)
        
        # Set icon
        try:
            if ICON_PATH.exists():
                self.root.iconbitmap(str(ICON_PATH))
        except:
            pass
        
        self.processes = {}
        self.config = self.load_config()
        
        self.build_ui()
    
    def load_config(self):
        """Load or create default config from settings.py"""
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return self.load_default_config()
    
    def load_default_config(self):
        """Load default config from settings.py"""
        default_config = {
            "camera_index": 0,
            "distance_far": 150,
            "distance_near": 300,
            "distance_very_near": 450,
            "stage2_countdown": 10,
            "stage3_timeout": 15,
            "stage4_idle_timeout": 15,
            "stage4_countdown": 60,
            "web_url": "http://localhost:5173",
            "fullscreen": False,
            "debug_mode": True
        }
        
        # Try to import from settings.py
        try:
            import sys
            from pathlib import Path
            config_dir = Path(__file__).parent / "config"
            if str(config_dir) not in sys.path:
                sys.path.insert(0, str(config_dir))
            import settings
            default_config["camera_index"] = getattr(settings, "CAMERA_INDEX", 0)
            default_config["distance_far"] = getattr(settings, "DISTANCE_FAR", 150)
            default_config["distance_near"] = getattr(settings, "DISTANCE_NEAR", 300)
            default_config["distance_very_near"] = getattr(settings, "DISTANCE_VERY_NEAR", 450)
            default_config["stage2_countdown"] = getattr(settings, "STAGE2_COUNTDOWN", 10)
            default_config["stage3_timeout"] = getattr(settings, "STAGE3_RESPONSE_TIMEOUT", 15)
            default_config["stage4_idle_timeout"] = getattr(settings, "STAGE4_IDLE_TIMEOUT", 15)
            default_config["stage4_countdown"] = getattr(settings, "STAGE4_COUNTDOWN_DURATION", 5)
            default_config["web_url"] = getattr(settings, "WEB_URL", "http://localhost:5173")
            default_config["fullscreen"] = getattr(settings, "FULLSCREEN_MODE", False)
            default_config["debug_mode"] = getattr(settings, "DEBUG_MODE", True)
        except Exception as e:
            print(f"Could not load from settings.py: {e}")
        
        return default_config
    
    def save_config(self, config):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    
    def build_ui(self):
        main_frame = tk.Frame(self.root, bg=BG_MAIN)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.build_header(main_frame)
        
        content_frame = tk.Frame(main_frame, bg=BG_MAIN)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        self.build_actions(content_frame)
        self.build_configuration(content_frame)
    
    def build_header(self, parent):
        header_frame = tk.Frame(parent, bg=HEADER_BG, height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Frame(header_frame, bg=BORDER_COLOR, height=1).pack(side=tk.BOTTOM, fill=tk.X)
        
        header_content = tk.Frame(header_frame, bg=HEADER_BG)
        header_content.pack(fill=tk.BOTH, expand=True, padx=50)
        
        tk.Label(header_content, 
                text="Kiosk Control Center", 
                font=("Segoe UI", 24, "bold"),
                fg=TEXT_PRIMARY, bg=HEADER_BG).pack(side=tk.LEFT, pady=20)
        
        # Logo
        if LOGO_PATH.exists() and HAS_PIL:
            try:
                logo_img = Image.open(LOGO_PATH)
                logo_img = logo_img.resize((81, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_content, image=logo_photo, bg=HEADER_BG)
                logo_label.image = logo_photo
                logo_label.pack(side=tk.RIGHT, pady=15)
            except Exception as e:
                print(f"Failed to load logo: {e}")
    
    def build_actions(self, parent):
        tk.Label(parent, text="Actions", 
                font=("Segoe UI", 18, "bold"),
                fg=TEXT_PRIMARY, bg=BG_MAIN).pack(anchor=tk.W, pady=(0, 20))
        
        btn_container = tk.Frame(parent, bg=BG_MAIN)
        btn_container.pack(fill=tk.X, pady=(0, 40))
        
        btn_container.grid_columnconfigure(0, weight=1)
        btn_container.grid_columnconfigure(1, weight=1)
        btn_container.grid_columnconfigure(2, weight=1)
        
        # Calibration Button
        calibrate_btn = ActionButton(btn_container, 
                                     "CALIBRATION",
                                     BTN_CALIBRATION,
                                     icon_name="monitor-cog",
                                     command=self.run_calibration,
                                     width=300, height=150)
        calibrate_btn.grid(row=0, column=0, padx=10, sticky="nsew")
        
        # Start Button
        start_btn = ActionButton(btn_container,
                                "START",
                                BTN_START,
                                icon_name="play",
                                command=self.start_kiosk,
                                width=300, height=150)
        start_btn.grid(row=0, column=1, padx=10, sticky="nsew")
        
        # Test Button
        test_btn = ActionButton(btn_container,
                               "TEST",
                               BTN_TEST,
                               icon_name="wrench",
                               command=self.run_test,
                               width=300, height=150)
        test_btn.grid(row=0, column=2, padx=10, sticky="nsew")
    
    def build_configuration(self, parent):
        config_header = tk.Frame(parent, bg=BG_MAIN)
        config_header.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(config_header, text="Configurations", 
                font=("Segoe UI", 18, "bold"),
                fg=TEXT_PRIMARY, bg=BG_MAIN).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(config_header, bg=BG_MAIN)
        btn_frame.pack(side=tk.RIGHT)
        
        reset_btn = SmallButton(btn_frame, "Reset", BTN_RESET,
                               icon_name="trash",
                               command=self.reset_config,
                               width=120, height=35)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = SmallButton(btn_frame, "Edit Data", BTN_EDIT,
                              icon_name="pencil",
                              command=self.edit_config,
                              width=130, height=35)
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        table_container = tk.Frame(parent, bg=BG_WHITE, relief=tk.SOLID, borderwidth=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        self.build_config_table(table_container)
    
    def build_config_table(self, parent):
        canvas = tk.Canvas(parent, bg=BG_WHITE, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_WHITE)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        
        def on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_resize)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Table header
        header_frame = tk.Frame(scrollable_frame, bg="#f8f9fa", height=40)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Frame(scrollable_frame, bg=BORDER_COLOR, height=1).pack(fill=tk.X)
        
        # Table rows
        self.value_labels = {}
        
        for key, label_text in CONFIG_LABELS.items():
            if key not in self.config:
                continue
            
            row_frame = tk.Frame(scrollable_frame, bg=BG_WHITE)
            row_frame.pack(fill=tk.X, padx=20, pady=12)
            
            row_frame.grid_columnconfigure(0, weight=3)   # Kolom 1
            row_frame.grid_columnconfigure(1, weight=3)   # Kolom 2
            row_frame.grid_columnconfigure(2, weight=6)   # Kolom 3
            
            # Label
            tk.Label(row_frame, text=label_text,
                    font=("Segoe UI", 11),
                    fg=TEXT_PRIMARY, bg=BG_WHITE,
                    anchor=tk.W).grid(row=0, column=0, sticky="w")
            
            # Value
            value = self.config[key]
            value_label = tk.Label(row_frame, text=str(value),
                                  font=("Segoe UI", 11, "bold"),
                                  fg=TEXT_PRIMARY, bg=BG_WHITE,
                                  anchor=tk.CENTER)
            value_label.grid(row=0, column=1, sticky="ew", padx=20)
            self.value_labels[key] = value_label
            
            # Description
            description = CONFIG_DESCRIPTIONS.get(key, "")
            tk.Label(row_frame, text=description,
                    font=("Segoe UI", 10),
                    fg=TEXT_SECONDARY, bg=BG_WHITE,
                    anchor=tk.W, wraplength=500,
                    justify=tk.LEFT).grid(row=0, column=2, sticky="w")
            
            tk.Frame(scrollable_frame, bg=BORDER_COLOR, height=1).pack(fill=tk.X, padx=20)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_config_display(self):
        for key, label in self.value_labels.items():
            if key in self.config:
                label.config(text=str(self.config[key]))
    
    def start_kiosk(self):
        if "main_app" in self.processes and self.processes["main_app"].poll() is None:
            messagebox.showwarning("Sudah Berjalan", 
                                  "Aplikasi kiosk sudah berjalan!")
            return
        
        if not MAIN_APP.exists():
            messagebox.showerror("Error", 
                               f"Aplikasi utama tidak ditemukan:\n{MAIN_APP}")
            return
        
        try:
            if sys.platform == "win32":
                cmd = f'start cmd /k python "{MAIN_APP}"'
                self.processes["main_app"] = subprocess.Popen(cmd, shell=True)
            else:
                cmd = ["x-terminal-emulator", "-e", f"python3 {MAIN_APP}"]
                self.processes["main_app"] = subprocess.Popen(cmd)
            
            messagebox.showinfo("Sukses", "Aplikasi kiosk berhasil dijalankan!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menjalankan aplikasi:\n{str(e)}")
    
    def run_calibration(self):
        if not CALIBRATION_TOOL.exists():
            messagebox.showerror("Error", 
                               f"Tool kalibrasi tidak ditemukan:\n{CALIBRATION_TOOL}")
            return
        
        try:
            if sys.platform == "win32":
                cmd = f'start cmd /k python "{CALIBRATION_TOOL}"'
                subprocess.Popen(cmd, shell=True)
            else:
                cmd = ["x-terminal-emulator", "-e", f"python3 {CALIBRATION_TOOL}"]
                subprocess.Popen(cmd)
            
            messagebox.showinfo("Info", 
                              "Tool kalibrasi dibuka.\n\n"
                              "Ikuti instruksi di layar.\n"
                              "Konfigurasi akan disimpan ke: config/data/settings.json")
            
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menjalankan kalibrasi:\n{str(e)}")
    
    def run_test(self):
        if not TEST_COMPONENTS.exists():
            messagebox.showerror("Error", 
                               f"Script test tidak ditemukan:\n{TEST_COMPONENTS}")
            return
        
        # Show running message
        def show_running_msg():
            msg = tk.Toplevel(self.root)
            msg.title("Menjalankan Test")
            msg.geometry("350x120")
            msg.configure(bg=BG_WHITE)
            msg.resizable(False, False)
            
            msg.transient(self.root)
            msg.grab_set()
            
            tk.Label(msg, text="Menjalankan test komponen...", 
                    font=("Segoe UI", 12, "bold"), 
                    fg=TEXT_PRIMARY, bg=BG_WHITE).pack(pady=(25, 10))
            tk.Label(msg, text="Mohon tunggu...", 
                    font=("Segoe UI", 10), 
                    fg=TEXT_SECONDARY, bg=BG_WHITE).pack()
            
            return msg
        
        running_window = show_running_msg()
        
        # Run test in background thread
        def run_test_thread():
            try:
                result = subprocess.run(
                    [sys.executable, str(TEST_COMPONENTS)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=str(BASE_DIR)
                )
                
                stdout = result.stdout
                stderr = result.stderr
                
                passed = stdout.count("PASSED")
                failed = stdout.count("FAILED")
                
                self.root.after(0, running_window.destroy)
                
                if failed == 0 and passed > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Hasil Test",
                        f"Semua Test Berhasil! ✓\n\n"
                        f"Lulus: {passed}\n"
                        f"Gagal: {failed}\n\n"
                        f"Sistem siap digunakan."
                    ))
                elif passed > 0 or failed > 0:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Hasil Test",
                        f"Beberapa Test Gagal ⚠\n\n"
                        f"Lulus: {passed}\n"
                        f"Gagal: {failed}\n\n"
                        f"Silakan periksa masalah yang ada."
                    ))
                else:
                    error_msg = stderr if stderr else "Terjadi kesalahan yang tidak diketahui"
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error Test",
                        f"Gagal menjalankan test:\n\n{error_msg[:300]}"
                    ))
                
            except subprocess.TimeoutExpired:
                self.root.after(0, running_window.destroy)
                self.root.after(0, lambda: messagebox.showerror(
                    "Test Timeout",
                    "Waktu eksekusi test habis (60 detik)"
                ))
            except Exception as e:
                self.root.after(0, running_window.destroy)
                self.root.after(0, lambda: messagebox.showerror(
                    "Error Test",
                    f"Gagal menjalankan test:\n\n{str(e)}"
                ))
        
        test_thread = threading.Thread(target=run_test_thread, daemon=True)
        test_thread.start()
    
    def edit_config(self):
        def on_save(new_config):
            self.config = new_config
            self.save_config(new_config)
            self.update_config_display()
            messagebox.showinfo("Sukses", 
                              "Konfigurasi berhasil disimpan!\n\n"
                              "Restart aplikasi untuk menerapkan perubahan.")
        
        EditConfigDialog(self.root, self.config, on_save)
    
    def reset_config(self):
        if messagebox.askyesno("Konfirmasi Reset", 
                               "Apakah Anda yakin ingin mereset konfigurasi?\n\n"
                               "Semua pengaturan akan kembali ke nilai default dari settings.py.\n"
                               "Tindakan ini tidak dapat dibatalkan!",
                               icon='warning'):
            
            default_config = self.load_default_config()
            
            self.config = default_config
            self.save_config(default_config)
            
            self.update_config_display()
            
            messagebox.showinfo("Reset Berhasil", 
                              "Konfigurasi telah direset ke nilai default!\n\n"
                              "Restart aplikasi untuk menerapkan perubahan.")
    
    def run(self):
        self.root.mainloop()
    
    def on_closing(self):
        for name, proc in self.processes.items():
            if proc.poll() is None:
                try:
                    proc.terminate()
                except:
                    pass
        
        self.root.destroy()


def main():
    try:
        app = ModernDashboard()
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.run()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Aplikasi gagal dijalankan:\n{str(e)}")


if __name__ == "__main__":
    main()