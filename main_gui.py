"""
C-Merch Kiosk - Modern Dashboard GUI
Redesigned with modern dark purple theme - Responsive Layout
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
import io

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Modern Dark Purple Theme
BG_DARK = "#1a1625"
BG_CARD = "#252037"
BG_SIDEBAR = "#1e1b2e"
PURPLE_PRIMARY = "#8b5cf6"
PURPLE_SECONDARY = "#a78bfa"
PURPLE_ACCENT = "#c084fc"
PINK_ACCENT = "#ec4899"
BLUE_ACCENT = "#3b82f6"
GREEN_ACCENT = "#10b981"
TEXT_PRIMARY = "#f3f4f6"
TEXT_SECONDARY = "#9ca3af"
TEXT_MUTED = "#6b7280"
BORDER_COLOR = "#374151"

# Paths
BASE_DIR = Path(__file__).parent
ICON_PATH = BASE_DIR / "assets" / "icon-c-merch-color.ico"
CONFIG_PATH = BASE_DIR / "config" / "kiosk_config.json"
SETTINGS_PATH = BASE_DIR / "settings.py"

# Scripts
MAIN_APP = BASE_DIR / "main.py"
CALIBRATION_TOOL = BASE_DIR / "utility" / "calibration_tool.py"
TEST_COMPONENTS = BASE_DIR / "utility" / "test_components.py"

# Icon paths
ICON_DIR = BASE_DIR / "assets" / "icons"
PLAY_ICON = ICON_DIR / "play.png"
CALIBRATE_ICON = ICON_DIR / "monitor-cog.png"
TEST_ICON = ICON_DIR / "wrench.png"


class ModernButton(tk.Canvas):
    """Modern button with hover effects"""
    
    def __init__(self, parent, text, icon_path=None, command=None, 
                 color=PURPLE_PRIMARY, **kwargs):
        super().__init__(parent, bg=BG_DARK, highlightthickness=0, **kwargs)
        
        self.text = text
        self.icon_path = icon_path
        self.command = command
        self.color = color
        self.is_hovered = False
        self.icon_image = None
        
        # Load icon if available
        if icon_path and Path(icon_path).exists() and HAS_PIL:
            self._load_icon()
        
        self.bind("<Configure>", self._on_resize)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _load_icon(self):
        """Load icon"""
        try:
            img = Image.open(self.icon_path)
            img = img.resize((24, 24), Image.Resampling.LANCZOS)
            self.icon_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Failed to load icon: {e}")
    
    def _on_resize(self, event=None):
        """Redraw on resize"""
        self.draw()
    
    def draw(self):
        """Draw button"""
        self.delete("all")
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Button background with hover effect
        color = self._adjust_color(self.color, 1.2) if self.is_hovered else self.color
        
        radius = 12
        self._create_rounded_rect(0, 0, width, height, radius, fill=color, outline="")
        
        # Calculate positions
        if self.icon_image:
            icon_x = 30
            icon_y = height // 2
            self.create_image(icon_x, icon_y, image=self.icon_image)
            text_x = icon_x + 40
            text_anchor = tk.W
        else:
            text_x = width // 2
            text_anchor = tk.CENTER
        
        # Draw text
        self.create_text(text_x, height // 2, text=self.text,
                        fill=TEXT_PRIMARY, anchor=text_anchor,
                        font=("Segoe UI", 11, "bold"))
    
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
        """Adjust color brightness"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
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


class StatusIndicator(tk.Canvas):
    """LED-style status indicator"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=16, height=16, 
                        bg=BG_CARD, highlightthickness=0, **kwargs)
        self.status = "off"
        self._draw()
    
    def _draw(self):
        self.delete("all")
        colors = {
            "off": "#555555",
            "ready": "#00FF00",
            "running": "#E6251C",
            "error": "#FF0000"
        }
        color = colors.get(self.status, "#555555")
        self.create_oval(2, 2, 14, 14, fill=color, outline=TEXT_PRIMARY, width=1)
    
    def set_status(self, status):
        self.status = status
        self._draw()


class ModernDashboard:
    """Main Dashboard Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("C-Merch Kiosk - Control Center")
        
        # Window settings - resizable
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=BG_DARK)
        
        # Set icon
        try:
            if ICON_PATH.exists():
                self.root.iconbitmap(str(ICON_PATH))
        except:
            pass
        
        # Running processes
        self.processes = {}
        
        # Load config
        self.config = self.load_config()
        
        # Build UI
        self.build_ui()
        
        # Update status
        self.update_status()
    
    def load_config(self):
        """Load or create default config"""
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Create default config
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
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config):
        """Save config to JSON"""
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    
    def build_ui(self):
        """Build the dashboard UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg=BG_DARK)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.build_header(main_frame)
        
        # Scrollable content
        self.build_content(main_frame)
        
        # Footer
        self.build_footer(main_frame)
    
    def build_header(self, parent):
        """Build header with title"""
        header_frame = tk.Frame(parent, bg=PURPLE_PRIMARY, height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, 
                               text="C-Merch", 
                               font=("Segoe UI", 28, "bold"),
                               fg=TEXT_PRIMARY, bg=PURPLE_PRIMARY)
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Kiosk Control Center", 
                                 font=("Segoe UI", 12),
                                 fg=PURPLE_ACCENT, bg=PURPLE_PRIMARY)
        subtitle_label.pack()
    
    def build_content(self, parent):
        """Build main content area"""
        # Create canvas for scrolling
        canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_DARK)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        
        # Update canvas window width on resize
        def on_canvas_resize(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_resize)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Status Section (NO CARDS)
        self.build_status_section(scrollable_frame)
        
        # Action Buttons Section
        self.build_actions_section(scrollable_frame)
        
        # Configuration Section
        self.build_config_section(scrollable_frame)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def build_status_section(self, parent):
        """Build system status section"""
        status_frame = tk.Frame(parent, bg=BG_CARD, relief=tk.FLAT)
        status_frame.pack(fill=tk.X, padx=30, pady=20)
        
        status_title = tk.Label(status_frame, text="SYSTEM STATUS", 
                               font=("Segoe UI", 12, "bold"),
                               fg=PURPLE_ACCENT, bg=BG_CARD)
        status_title.pack(pady=15)
        
        # Status indicators
        self.status_items = {}
        status_data = [
            ("Main App", "main_app"),
            ("Camera", "camera"),
            ("YOLO Model", "yolo"),
            ("Configuration", "config")
        ]
        
        for label, key in status_data:
            item_frame = tk.Frame(status_frame, bg=BG_CARD)
            item_frame.pack(fill=tk.X, padx=30, pady=8)
            
            indicator = StatusIndicator(item_frame)
            indicator.pack(side=tk.LEFT, padx=(0, 15))
            
            text_label = tk.Label(item_frame, text=label, 
                                 font=("Segoe UI", 11),
                                 fg=TEXT_SECONDARY, bg=BG_CARD, anchor=tk.W)
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.status_items[key] = indicator
        
        tk.Frame(status_frame, bg=BG_CARD, height=15).pack()
    
    def build_actions_section(self, parent):
        """Build action buttons section"""
        action_frame = tk.Frame(parent, bg=BG_DARK)
        action_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        action_label = tk.Label(action_frame, text="QUICK ACTIONS", 
                               font=("Segoe UI", 12, "bold"),
                               fg=PURPLE_ACCENT, bg=BG_DARK)
        action_label.pack(pady=(0, 20))
        
        # Start Kiosk Button
        start_btn = ModernButton(action_frame, 
                                text="START KIOSK",
                                icon_path=PLAY_ICON,
                                command=self.start_kiosk,
                                color=GREEN_ACCENT)
        start_btn.pack(fill=tk.X, pady=10, ipady=20)
        
        # Other buttons in grid
        btn_frame = tk.Frame(action_frame, bg=BG_DARK)
        btn_frame.pack(fill=tk.X, pady=10)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        calibrate_btn = ModernButton(btn_frame,
                                     text="CALIBRATION",
                                     icon_path=CALIBRATE_ICON,
                                     command=self.run_calibration,
                                     color=BLUE_ACCENT)
        calibrate_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10), ipady=15)
        
        test_btn = ModernButton(btn_frame,
                               text="TEST SYSTEM",
                               icon_path=TEST_ICON,
                               command=self.run_test,
                               color=PURPLE_PRIMARY)
        test_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0), ipady=15)
    
    def build_config_section(self, parent):
        """Build configuration section"""
        config_frame = tk.Frame(parent, bg=BG_CARD, relief=tk.FLAT)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(15, 30))
        
        config_title = tk.Label(config_frame, text="CONFIGURATION", 
                               font=("Segoe UI", 12, "bold"),
                               fg=PURPLE_ACCENT, bg=BG_CARD)
        config_title.pack(pady=15)
        
        # Config display
        config_display_frame = tk.Frame(config_frame, bg="#3b0ac2", relief=tk.FLAT)
        config_display_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 15))
        
        canvas = tk.Canvas(config_display_frame, bg="#1a1625", 
                          highlightthickness=0, height=250)
        scrollbar = tk.Scrollbar(config_display_frame, orient=tk.VERTICAL, 
                                command=canvas.yview)
        scrollable = tk.Frame(canvas, bg="#1a1625")
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display config items
        self.config_labels = {}
        for key, value in self.config.items():
            item_frame = tk.Frame(scrollable, bg="#1a1625")
            item_frame.pack(fill=tk.X, padx=15, pady=8)
            
            key_label = tk.Label(item_frame, 
                                text=key.replace('_', ' ').title() + ":",
                                font=("Segoe UI", 10),
                                fg=PURPLE_ACCENT, bg="#1a1625",
                                anchor=tk.W, width=20)
            key_label.pack(side=tk.LEFT, padx=(0, 10))
            
            value_label = tk.Label(item_frame,
                                  text=str(value),
                                  font=("Segoe UI", 10),
                                  fg=TEXT_PRIMARY, bg="#1a1625",
                                  anchor=tk.W)
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.config_labels[key] = value_label
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Edit button
        edit_btn = ModernButton(config_frame,
                               text="Edit Configuration",
                               command=self.edit_config,
                               color="#4b5563")
        edit_btn.pack(fill=tk.X, pady=15, ipady=10)
    
    def build_footer(self, parent):
        """Build footer"""
        footer_frame = tk.Frame(parent, bg=PURPLE_PRIMARY, height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, 
                               text=f"2024 C-Merch | {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                               font=("Segoe UI", 9),
                               fg=TEXT_SECONDARY, bg=PURPLE_PRIMARY)
        footer_label.pack(expand=True)
    
    def update_config_display(self):
        """Update config display"""
        for key, label in self.config_labels.items():
            if key in self.config:
                label.config(text=str(self.config[key]))
    
    def update_status(self):
        """Update status indicators"""
        main_exists = MAIN_APP.exists()
        self.status_items["main_app"].set_status("ready" if main_exists else "error")
        
        self.status_items["camera"].set_status("ready")
        
        yolo_path = BASE_DIR / "yolov5n.pt"
        self.status_items["yolo"].set_status("ready" if yolo_path.exists() else "off")
        
        config_exists = CONFIG_PATH.exists()
        self.status_items["config"].set_status("ready" if config_exists else "error")
    
    def start_kiosk(self):
        """Start main kiosk application"""
        if "main_app" in self.processes and self.processes["main_app"].poll() is None:
            messagebox.showwarning("Already Running", 
                                  "Kiosk application is already running!")
            return
        
        if not MAIN_APP.exists():
            messagebox.showerror("Error", 
                               f"Main application not found:\n{MAIN_APP}")
            return
        
        try:
            if sys.platform == "win32":
                cmd = f'start cmd /k python "{MAIN_APP}"'
                self.processes["main_app"] = subprocess.Popen(cmd, shell=True)
            else:
                cmd = ["x-terminal-emulator", "-e", f"python3 {MAIN_APP}"]
                self.processes["main_app"] = subprocess.Popen(cmd)
            
            self.status_items["main_app"].set_status("running")
            messagebox.showinfo("Success", "Kiosk application started!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application:\n{str(e)}")
    
    def run_calibration(self):
        """Run calibration tool"""
        if not CALIBRATION_TOOL.exists():
            messagebox.showerror("Error", 
                               f"Calibration tool not found:\n{CALIBRATION_TOOL}")
            return
        
        try:
            if sys.platform == "win32":
                cmd = f'start cmd /k python "{CALIBRATION_TOOL}"'
                subprocess.Popen(cmd, shell=True)
            else:
                cmd = ["x-terminal-emulator", "-e", f"python3 {CALIBRATION_TOOL}"]
                subprocess.Popen(cmd)
            
            messagebox.showinfo("Info", 
                              "Calibration tool opened.\n"
                              "Follow on-screen instructions.\n"
                              "Config saved to: config/kiosk_config.json")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start calibration:\n{str(e)}")
    
    def run_test(self):
        """Run component tests in background"""
        if not TEST_COMPONENTS.exists():
            messagebox.showerror("Error", 
                               f"Test script not found:\n{TEST_COMPONENTS}")
            return
        
        # Show initial message
        def show_running_msg():
            msg = tk.Toplevel(self.root)
            msg.title("Running Tests")
            msg.geometry("300x100")
            msg.configure(bg=BG_CARD)
            msg.resizable(False, False)
            
            # Center window
            msg.transient(self.root)
            msg.grab_set()
            
            tk.Label(msg, text="Running component tests...", 
                    font=("Segoe UI", 11), fg=TEXT_PRIMARY, bg=BG_CARD).pack(pady=20)
            tk.Label(msg, text="Please wait...", 
                    font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_CARD).pack()
            
            return msg
        
        running_window = show_running_msg()
        
        # Run test in background
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
                
                # Parse results
                passed = stdout.count("PASSED")
                failed = stdout.count("FAILED")
                
                # Close running window
                self.root.after(0, running_window.destroy)
                
                # Show results
                if failed == 0 and passed > 0:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Test Results",
                        f"All Tests Passed!\n\n"
                        f"Passed: {passed}\n"
                        f"Failed: {failed}\n\n"
                        f"System ready to run."
                    ))
                elif passed > 0 or failed > 0:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "Test Results",
                        f"Some Tests Failed\n\n"
                        f"Passed: {passed}\n"
                        f"Failed: {failed}\n\n"
                        f"Please check the issues."
                    ))
                else:
                    error_msg = stderr if stderr else "Unknown error occurred"
                    self.root.after(0, lambda: messagebox.showerror(
                        "Test Error",
                        f"Failed to run tests:\n\n{error_msg[:300]}"
                    ))
                
            except subprocess.TimeoutExpired:
                self.root.after(0, running_window.destroy)
                self.root.after(0, lambda: messagebox.showerror(
                    "Test Timeout",
                    "Test execution timeout (60 seconds)"
                ))
            except Exception as e:
                self.root.after(0, running_window.destroy)
                self.root.after(0, lambda: messagebox.showerror(
                    "Test Error",
                    f"Failed to run tests:\n\n{str(e)}"
                ))
        
        # Start thread
        test_thread = threading.Thread(target=run_test_thread, daemon=True)
        test_thread.start()
    
    def edit_config(self):
        """Open config file in default editor"""
        try:
            if sys.platform == "win32":
                os.startfile(CONFIG_PATH)
            elif sys.platform == "darwin":
                subprocess.call(["open", CONFIG_PATH])
            else:
                subprocess.call(["xdg-open", CONFIG_PATH])
            
            messagebox.showinfo("Info", 
                              "Config file opened.\n"
                              "Restart app to apply changes.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open config:\n{str(e)}")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        for name, proc in self.processes.items():
            if proc.poll() is None:
                try:
                    proc.terminate()
                except:
                    pass
        
        self.root.destroy()


def main():
    """Entry point"""
    try:
        app = ModernDashboard()
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")


if __name__ == "__main__":
    main()