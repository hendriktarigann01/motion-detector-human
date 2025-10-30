"""
MJ Solution Kiosk - GUI Launcher (Compact Version)
Modern dashboard untuk control kiosk application - Laptop Friendly
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Brand Colors
COMMUTER_RED = "#E6251C"
METRO_BLUE = "#252271"
DARK_BG = "#1a1a1a"
LIGHT_BG = "#2a2a2a"
ACCENT_CYAN = "#00C8FF"
TEXT_WHITE = "#FFFFFF"
TEXT_GRAY = "#CCCCCC"

# Paths
BASE_DIR = Path(__file__).parent
ICON_PATH = BASE_DIR / "assets" / "icon-c-merch-color.ico"
CONFIG_PATH = BASE_DIR / "config" / "kiosk_config.json"
SETTINGS_PATH = BASE_DIR / "config" / "settings.py"

# Scripts
MAIN_APP = BASE_DIR / "main.py"
CALIBRATION_TOOL = BASE_DIR / "utility" / "calibration_tool.py"
TEST_COMPONENTS = BASE_DIR / "utility" / "test_components.py"


class ModernButton(tk.Canvas):
    """Custom modern button dengan hover effect"""
    
    def __init__(self, parent, text, command, width=200, height=50, 
                 bg_color=COMMUTER_RED, hover_color="#FF3020", **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=DARK_BG, highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text = text
        self.width = width
        self.height = height
        
        self._draw_button(bg_color)
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
    
    def _draw_button(self, color):
        """Draw button shape"""
        self.delete("all")
        
        # Rounded rectangle
        radius = 12
        self.create_rounded_rect(3, 3, self.width-3, self.height-3, 
                                radius, fill=color, outline=ACCENT_CYAN, width=2)
        
        # Text
        font_size = 11 if self.height > 60 else 10
        self.create_text(self.width//2, self.height//2, 
                        text=self.text, fill=TEXT_WHITE, 
                        font=("Segoe UI", font_size, "bold"))
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Create rounded rectangle"""
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self._draw_button(self.hover_color)
        self.config(cursor="hand2")
    
    def _on_leave(self, event):
        self._draw_button(self.bg_color)
        self.config(cursor="")
    
    def _on_click(self, event):
        if self.command:
            self.command()


class StatusIndicator(tk.Canvas):
    """LED-style status indicator"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, width=16, height=16, 
                        bg=DARK_BG, highlightthickness=0, **kwargs)
        self.status = "off"
        self._draw()
    
    def _draw(self):
        self.delete("all")
        colors = {
            "off": "#555555",
            "ready": "#00FF00",
            "running": COMMUTER_RED,
            "error": "#FF0000"
        }
        color = colors.get(self.status, "#555555")
        self.create_oval(2, 2, 14, 14, fill=color, outline=TEXT_WHITE, width=1)
    
    def set_status(self, status):
        self.status = status
        self._draw()


class KioskLauncher:
    """Main Launcher Application - Compact Version"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MJ Solution Kiosk - Control Center")
        self.root.geometry("700x650")  # COMPACT: 700x650 (was 800x900)
        self.root.resizable(False, False)
        self.root.configure(bg=DARK_BG)
        
        # Set icon
        try:
            if ICON_PATH.exists():
                self.root.iconbitmap(str(ICON_PATH))
        except:
            pass
        
        # Running processes
        self.processes = {}
        
        # Load or create config
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
        
        # Create default config from settings.py
        default_config = {
            "camera_index": 1,
            "distance_far": 150,
            "distance_near": 450,
            "distance_very_near": 700,
            "stage2_countdown": 10,
            "stage3_timeout": 15,
            "stage4_idle_timeout": 15,
            "stage4_countdown": 60,
            "web_url": "http://localhost:5173",
            "fullscreen": False,
            "debug_mode": True
        }
        
        # Save default
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config):
        """Save config to JSON"""
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    
    def build_ui(self):
        """Build the user interface"""
        # Header - COMPACT
        header_frame = tk.Frame(self.root, bg=METRO_BLUE, height=90)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo/Title
        title_label = tk.Label(header_frame, 
                               text="MJ SOLUTION", 
                               font=("Segoe UI", 22, "bold"),  # Smaller: 22 (was 32)
                               fg=TEXT_WHITE, bg=METRO_BLUE)
        title_label.pack(pady=12)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Kiosk Control Center", 
                                 font=("Segoe UI", 10),  # Smaller: 10 (was 14)
                                 fg=ACCENT_CYAN, bg=METRO_BLUE)
        subtitle_label.pack()
        
        # Main container - COMPACT padding
        main_frame = tk.Frame(self.root, bg=DARK_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Status Section - COMPACT
        status_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.RIDGE, bd=2)
        status_frame.pack(fill=tk.X, pady=(0, 12))
        
        status_title = tk.Label(status_frame, text="SYSTEM STATUS", 
                               font=("Segoe UI", 10, "bold"),  # Smaller: 10
                               fg=ACCENT_CYAN, bg=LIGHT_BG)
        status_title.pack(pady=6)
        
        # Status indicators - COMPACT
        self.status_items = {}
        status_data = [
            ("Main App", "main_app"),
            ("Camera", "camera"),
            ("YOLO", "yolo"),
            ("Config", "config")
        ]
        
        for label, key in status_data:
            item_frame = tk.Frame(status_frame, bg=LIGHT_BG)
            item_frame.pack(fill=tk.X, padx=15, pady=3)
            
            indicator = StatusIndicator(item_frame)
            indicator.pack(side=tk.LEFT, padx=(0, 8))
            
            text_label = tk.Label(item_frame, text=label, 
                                 font=("Segoe UI", 9),  # Smaller: 9
                                 fg=TEXT_GRAY, bg=LIGHT_BG, anchor=tk.W)
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.status_items[key] = indicator
        
        # Spacer
        tk.Frame(main_frame, bg=DARK_BG, height=8).pack()
        
        # Action Buttons
        action_label = tk.Label(main_frame, text="QUICK ACTIONS", 
                               font=("Segoe UI", 10, "bold"),  # Smaller: 10
                               fg=ACCENT_CYAN, bg=DARK_BG)
        action_label.pack(pady=(8, 12))
        
        # Start Button (Big & Prominent) - COMPACT
        start_btn = ModernButton(main_frame, 
                                text="START KIOSK",
                                command=self.start_kiosk,
                                width=320, height=65,  # Smaller: 320x65 (was 400x100)
                                bg_color=COMMUTER_RED,
                                hover_color="#FF3020")
        start_btn.pack(pady=8)
        
        # Other buttons - COMPACT
        buttons_frame = tk.Frame(main_frame, bg=DARK_BG)
        buttons_frame.pack(pady=12)
        
        calibrate_btn = ModernButton(buttons_frame,
                                     text="CALIBRATION",
                                     command=self.run_calibration,
                                     width=200, height=50,  # Smaller: 200x50
                                     bg_color=METRO_BLUE,
                                     hover_color="#3232A1")
        calibrate_btn.pack(side=tk.LEFT, padx=8)
        
        test_btn = ModernButton(buttons_frame,
                               text="TEST",
                               command=self.run_test,
                               width=200, height=50,  # Smaller: 200x50
                               bg_color=METRO_BLUE,
                               hover_color="#3232A1")
        test_btn.pack(side=tk.LEFT, padx=8)
        
        # Config Section - COMPACT
        config_frame = tk.Frame(main_frame, bg=LIGHT_BG, relief=tk.RIDGE, bd=2)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))
        
        config_title = tk.Label(config_frame, text="CONFIGURATION", 
                               font=("Segoe UI", 10, "bold"),  # Smaller: 10
                               fg=ACCENT_CYAN, bg=LIGHT_BG)
        config_title.pack(pady=6)
        
        # Config display (scrollable) - COMPACT
        config_text_frame = tk.Frame(config_frame, bg=LIGHT_BG)
        config_text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 8))
        
        self.config_text = tk.Text(config_text_frame, 
                                   height=6,  # Smaller: 6 lines (was 8)
                                   font=("Consolas", 8),  # Smaller: 8 (was 9)
                                   bg="#2d2d2d", 
                                   fg=TEXT_WHITE,
                                   relief=tk.FLAT,
                                   padx=8, pady=6)
        self.config_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(config_text_frame, command=self.config_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.config_text.config(yscrollcommand=scrollbar.set)
        
        # Display config
        self.update_config_display()
        
        # Edit config button - COMPACT
        edit_btn = ModernButton(config_frame,
                               text="📝 Edit Config",
                               command=self.edit_config,
                               width=160, height=40,  # Smaller: 160x40
                               bg_color="#444444",
                               hover_color="#555555")
        edit_btn.pack(pady=8)
        
        # Footer - COMPACT
        footer_frame = tk.Frame(self.root, bg=METRO_BLUE, height=35)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, 
                               text=f"© 2024 MJ Solution • {datetime.now().strftime('%Y-%m-%d')}",
                               font=("Segoe UI", 8),  # Smaller: 8
                               fg=TEXT_GRAY, bg=METRO_BLUE)
        footer_label.pack(expand=True)
    
    def update_config_display(self):
        """Update config text display"""
        self.config_text.delete(1.0, tk.END)
        config_str = json.dumps(self.config, indent=2)
        self.config_text.insert(1.0, config_str)
        self.config_text.config(state=tk.DISABLED)
    
    def update_status(self):
        """Update status indicators"""
        # Check main app
        main_exists = MAIN_APP.exists()
        self.status_items["main_app"].set_status("ready" if main_exists else "error")
        
        # Check camera (dummy check - can't really check without opening)
        self.status_items["camera"].set_status("ready")
        
        # Check YOLO model
        yolo_path = BASE_DIR / "yolov5s.pt"
        self.status_items["yolo"].set_status("ready" if yolo_path.exists() else "off")
        
        # Check config
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
            # Start in new terminal
            if sys.platform == "win32":
                # Windows
                cmd = f'start cmd /k python "{MAIN_APP}"'
                self.processes["main_app"] = subprocess.Popen(cmd, shell=True)
            else:
                # Linux/Mac
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
        """Run component tests"""
        if not TEST_COMPONENTS.exists():
            messagebox.showerror("Error", 
                               f"Test script not found:\n{TEST_COMPONENTS}")
            return
        
        try:
            if sys.platform == "win32":
                cmd = f'start cmd /k python "{TEST_COMPONENTS}"'
                subprocess.Popen(cmd, shell=True)
            else:
                cmd = ["x-terminal-emulator", "-e", f"python3 {TEST_COMPONENTS}"]
                subprocess.Popen(cmd)
            
            messagebox.showinfo("Info", "Component test started.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start test:\n{str(e)}")
    
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
        # Close any running processes
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
        app = KioskLauncher()
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")


if __name__ == "__main__":
    main()