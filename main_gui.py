# """
# MJ Solution Kiosk - Modern GUI Application
# Eye-catching control panel for 1920x1080 display
# """

# import tkinter as tk
# from tkinter import ttk, messagebox
# import threading
# import sys
# import os
# from pathlib import Path
# import json
# import subprocess

# # Add project root to path
# sys.path.append(str(Path(__file__).parent))

# class ModernKioskGUI:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("MJ Solution Kiosk")
#         self.root.geometry("1920x1080")
#         self.root.configure(bg="#0f0f23")
        
#         # Make fullscreen
#         self.root.attributes('-fullscreen', True)
#         self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
#         self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', True))
        
#         # Variables
#         self.kiosk_running = False
#         self.kiosk_thread = None
        
#         # Config
#         self.config_file = "config/kiosk_config.json"
#         self.load_config()
        
#         # Colors
#         self.colors = {
#             'bg': '#0f0f23',
#             'card': '#1a1a2e',
#             'accent': '#00d4ff',
#             'success': '#00ff88',
#             'danger': '#ff3366',
#             'warning': '#ffd700',
#             'text': '#ffffff',
#             'text_dim': '#8892b0'
#         }
        
#         self.create_widgets()
        
#     def load_config(self):
#         """Load configuration"""
#         default_config = {
#             "camera_index": 1,
#             "camera_width": 1080,
#             "camera_height": 1920,
#             "distance_far": 200,
#             "distance_near": 400,
#             "distance_very_near": 700,
#             "stage2_countdown": 10,
#             "stage3_timeout": 15,
#             "stage4_idle_timeout": 15,
#             "stage4_countdown": 5,
#             "web_url": "https://mjsolution.co.id/our-product/",
#             "fullscreen": True,
#             "debug_mode": False
#         }
        
#         try:
#             if Path(self.config_file).exists():
#                 with open(self.config_file, 'r') as f:
#                     self.config = json.load(f)
#             else:
#                 self.config = default_config
#                 self.save_config()
#         except:
#             self.config = default_config
    
#     def save_config(self):
#         """Save configuration"""
#         try:
#             os.makedirs("config", exist_ok=True)
#             with open(self.config_file, 'w') as f:
#                 json.dump(self.config, f, indent=4)
#         except Exception as e:
#             messagebox.showerror("Error", f"Failed to save: {e}")
    
#     def create_widgets(self):
#         """Create modern UI"""
        
#         # Header
#         header = tk.Frame(self.root, bg=self.colors['card'], height=120)
#         header.pack(fill=tk.X, padx=20, pady=20)
#         header.pack_propagate(False)
        
#         title = tk.Label(
#             header,
#             text="🖥️ MJ KIOSK CONTROL",
#             font=("Segoe UI", 48, "bold"),
#             bg=self.colors['card'],
#             fg=self.colors['accent']
#         )
#         title.pack(side=tk.LEFT, padx=40, pady=30)
        
#         # Status indicator
#         self.status_indicator = tk.Label(
#             header,
#             text="● READY",
#             font=("Segoe UI", 24, "bold"),
#             bg=self.colors['card'],
#             fg=self.colors['text_dim']
#         )
#         self.status_indicator.pack(side=tk.RIGHT, padx=40, pady=30)
        
#         # Main content area
#         content = tk.Frame(self.root, bg=self.colors['bg'])
#         content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
#         # Left panel - Main Control
#         left_panel = tk.Frame(content, bg=self.colors['bg'])
#         left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
#         self.create_main_control(left_panel)
#         self.create_quick_actions(left_panel)
        
#         # Right panel - Settings
#         right_panel = tk.Frame(content, bg=self.colors['bg'])
#         right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
#         self.create_settings_panel(right_panel)
    
#     def create_main_control(self, parent):
#         """Main control card"""
#         card = tk.Frame(parent, bg=self.colors['card'], relief=tk.FLAT, bd=0)
#         card.pack(fill=tk.X, pady=(0, 20))
        
#         # Big start button
#         self.start_btn = tk.Button(
#             card,
#             text="▶️ START KIOSK",
#             font=("Segoe UI", 36, "bold"),
#             bg=self.colors['success'],
#             fg=self.colors['bg'],
#             activebackground=self.colors['accent'],
#             activeforeground=self.colors['bg'],
#             relief=tk.FLAT,
#             bd=0,
#             cursor="hand2",
#             command=self.toggle_kiosk
#         )
#         self.start_btn.pack(fill=tk.X, padx=40, pady=40)
        
#         # System info
#         info_frame = tk.Frame(card, bg=self.colors['card'])
#         info_frame.pack(fill=tk.X, padx=40, pady=(0, 30))
        
#         self.create_info_label(info_frame, "Camera", str(self.config.get("camera_index", 1)), 0)
#         self.create_info_label(info_frame, "Resolution", "1920x1080", 1)
#         self.create_info_label(info_frame, "Mode", "Production" if self.config.get("fullscreen") else "Debug", 2)
    
#     def create_info_label(self, parent, title, value, col):
#         """Create info label"""
#         frame = tk.Frame(parent, bg=self.colors['card'])
#         frame.grid(row=0, column=col, padx=20, sticky='ew')
#         parent.columnconfigure(col, weight=1)
        
#         tk.Label(
#             frame,
#             text=title,
#             font=("Segoe UI", 14),
#             bg=self.colors['card'],
#             fg=self.colors['text_dim']
#         ).pack()
        
#         tk.Label(
#             frame,
#             text=value,
#             font=("Segoe UI", 20, "bold"),
#             bg=self.colors['card'],
#             fg=self.colors['text']
#         ).pack()
    
#     def create_quick_actions(self, parent):
#         """Quick action buttons"""
#         card = tk.Frame(parent, bg=self.colors['card'])
#         card.pack(fill=tk.BOTH, expand=True)
        
#         tk.Label(
#             card,
#             text="QUICK ACTIONS",
#             font=("Segoe UI", 20, "bold"),
#             bg=self.colors['card'],
#             fg=self.colors['text']
#         ).pack(pady=(30, 20))
        
#         btn_container = tk.Frame(card, bg=self.colors['card'])
#         btn_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
#         actions = [
#             ("📹", "Detect\nCamera", self.detect_cameras, self.colors['accent']),
#             ("📏", "Calibrate\nDistance", self.calibrate_distance, self.colors['warning']),
#             ("🧪", "Test\nSystem", self.test_components, "#9d4edd"),
#             ("🎬", "Check\nMedia", self.check_media_files, "#06ffa5"),
#             ("📝", "View\nLogs", self.view_logs, "#ff006e"),
#             ("⚙️", "Save\nConfig", self.save_settings, self.colors['success'])
#         ]
        
#         for i, (icon, text, command, color) in enumerate(actions):
#             row = i // 3
#             col = i % 3
            
#             btn = tk.Button(
#                 btn_container,
#                 text=f"{icon}\n{text}",
#                 font=("Segoe UI", 16, "bold"),
#                 bg=color,
#                 fg=self.colors['bg'],
#                 activebackground=self.colors['text'],
#                 activeforeground=self.colors['bg'],
#                 relief=tk.FLAT,
#                 bd=0,
#                 cursor="hand2",
#                 command=command
#             )
#             btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
#             btn_container.rowconfigure(row, weight=1)
#             btn_container.columnconfigure(col, weight=1)
    
#     def create_settings_panel(self, parent):
#         """Settings panel"""
#         card = tk.Frame(parent, bg=self.colors['card'])
#         card.pack(fill=tk.BOTH, expand=True)
        
#         # Header
#         tk.Label(
#             card,
#             text="SETTINGS",
#             font=("Segoe UI", 20, "bold"),
#             bg=self.colors['card'],
#             fg=self.colors['text']
#         ).pack(pady=(30, 20))
        
#         # Scrollable settings
#         canvas = tk.Canvas(card, bg=self.colors['card'], highlightthickness=0)
#         scrollbar = tk.Scrollbar(card, orient="vertical", command=canvas.yview)
#         scrollable_frame = tk.Frame(canvas, bg=self.colors['card'])
        
#         scrollable_frame.bind(
#             "<Configure>",
#             lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
#         )
        
#         canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
#         canvas.configure(yscrollcommand=scrollbar.set)
        
#         # Camera settings
#         self.add_setting_section(scrollable_frame, "CAMERA", [
#             ("Camera Index", "camera_index", 0, 10, "0=built-in, 1+=external")
#         ])
        
#         # Distance settings
#         self.add_setting_section(scrollable_frame, "DISTANCE (pixels)", [
#             ("FAR (>5m)", "distance_far", 50, 500, "bbox height < X"),
#             ("NEAR (<5m)", "distance_near", 100, 700, "bbox height > X"),
#             ("VERY NEAR (≤0.6m)", "distance_very_near", 200, 1000, "bbox height > X")
#         ])
        
#         # Timeout settings
#         self.add_setting_section(scrollable_frame, "TIMEOUTS (seconds)", [
#             ("Stage 2 Countdown", "stage2_countdown", 5, 30, "person leaves"),
#             ("Stage 3 Timeout", "stage3_timeout", 10, 60, "no response"),
#             ("Stage 4 Idle", "stage4_idle_timeout", 10, 60, "no interaction"),
#             ("Stage 4 Countdown", "stage4_countdown", 3, 20, "before reset")
#         ])
        
#         # Advanced
#         advanced_frame = tk.Frame(scrollable_frame, bg=self.colors['card'])
#         advanced_frame.pack(fill=tk.X, padx=30, pady=20)
        
#         tk.Label(
#             advanced_frame,
#             text="Web URL:",
#             font=("Segoe UI", 14),
#             bg=self.colors['card'],
#             fg=self.colors['text_dim']
#         ).pack(anchor='w', pady=(0, 5))
        
#         self.web_url_var = tk.StringVar(value=self.config.get("web_url", ""))
#         url_entry = tk.Entry(
#             advanced_frame,
#             textvariable=self.web_url_var,
#             font=("Segoe UI", 12),
#             bg=self.colors['bg'],
#             fg=self.colors['text'],
#             insertbackground=self.colors['accent'],
#             relief=tk.FLAT,
#             bd=0
#         )
#         url_entry.pack(fill=tk.X, ipady=10)
        
#         # Checkboxes
#         self.fullscreen_var = tk.BooleanVar(value=self.config.get("fullscreen", True))
#         self.debug_var = tk.BooleanVar(value=self.config.get("debug_mode", False))
        
#         tk.Checkbutton(
#             advanced_frame,
#             text="Fullscreen Mode",
#             variable=self.fullscreen_var,
#             font=("Segoe UI", 14),
#             bg=self.colors['card'],
#             fg=self.colors['text'],
#             selectcolor=self.colors['bg'],
#             activebackground=self.colors['card'],
#             activeforeground=self.colors['accent']
#         ).pack(anchor='w', pady=10)
        
#         tk.Checkbutton(
#             advanced_frame,
#             text="Debug Mode",
#             variable=self.debug_var,
#             font=("Segoe UI", 14),
#             bg=self.colors['card'],
#             fg=self.colors['text'],
#             selectcolor=self.colors['bg'],
#             activebackground=self.colors['card'],
#             activeforeground=self.colors['accent']
#         ).pack(anchor='w', pady=10)
        
#         canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(30, 0), pady=(0, 30))
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 30), padx=(0, 20))
    
#     def add_setting_section(self, parent, title, settings):
#         """Add settings section"""
#         section = tk.Frame(parent, bg=self.colors['card'])
#         section.pack(fill=tk.X, padx=30, pady=10)
        
#         tk.Label(
#             section,
#             text=title,
#             font=("Segoe UI", 16, "bold"),
#             bg=self.colors['card'],
#             fg=self.colors['accent']
#         ).pack(anchor='w', pady=(10, 15))
        
#         for label, key, min_val, max_val, hint in settings:
#             frame = tk.Frame(section, bg=self.colors['card'])
#             frame.pack(fill=tk.X, pady=8)
            
#             tk.Label(
#                 frame,
#                 text=label,
#                 font=("Segoe UI", 13),
#                 bg=self.colors['card'],
#                 fg=self.colors['text']
#             ).pack(side=tk.LEFT)
            
#             var = tk.IntVar(value=self.config.get(key, min_val))
#             setattr(self, f"{key}_var", var)
            
#             spin = tk.Spinbox(
#                 frame,
#                 from_=min_val,
#                 to=max_val,
#                 textvariable=var,
#                 font=("Segoe UI", 12),
#                 bg=self.colors['bg'],
#                 fg=self.colors['text'],
#                 buttonbackground=self.colors['accent'],
#                 relief=tk.FLAT,
#                 bd=0,
#                 width=10
#             )
#             spin.pack(side=tk.RIGHT, padx=(10, 0))
            
#             tk.Label(
#                 frame,
#                 text=f"({hint})",
#                 font=("Segoe UI", 10),
#                 bg=self.colors['card'],
#                 fg=self.colors['text_dim']
#             ).pack(side=tk.RIGHT, padx=10)
    
#     def toggle_kiosk(self):
#         """Start/Stop kiosk"""
#         if not self.kiosk_running:
#             self.save_settings()
#             self.start_btn.config(
#                 text="⏹️ STOP KIOSK",
#                 bg=self.colors['danger']
#             )
#             self.status_indicator.config(
#                 text="● RUNNING",
#                 fg=self.colors['success']
#             )
#             self.kiosk_running = True
            
#             self.kiosk_thread = threading.Thread(target=self.run_kiosk, daemon=True)
#             self.kiosk_thread.start()
#         else:
#             self.kiosk_running = False
#             self.start_btn.config(
#                 text="▶️ START KIOSK",
#                 bg=self.colors['success']
#             )
#             self.status_indicator.config(
#                 text="● STOPPED",
#                 fg=self.colors['danger']
#             )
    
#     def run_kiosk(self):
#         """Run kiosk application"""
#         try:
#             from main import KioskApplication
#             self.apply_config()
#             app = KioskApplication()
#             app.run()
#         except Exception as e:
#             messagebox.showerror("Error", f"Kiosk error:\n{e}")
#             self.kiosk_running = False
#             self.start_btn.config(text="▶️ START KIOSK", bg=self.colors['success'])
    
#     def apply_config(self):
#         """Apply configuration to settings"""
#         from config import settings
#         settings.CAMERA_INDEX = self.camera_index_var.get()
#         settings.CAMERA_WIDTH = 1080
#         settings.CAMERA_HEIGHT = 1920
#         settings.DISTANCE_FAR = self.distance_far_var.get()
#         settings.DISTANCE_NEAR = self.distance_near_var.get()
#         settings.DISTANCE_VERY_NEAR = self.distance_very_near_var.get()
#         settings.STAGE2_COUNTDOWN = self.stage2_countdown_var.get()
#         settings.STAGE3_RESPONSE_TIMEOUT = self.stage3_timeout_var.get()
#         settings.STAGE4_IDLE_TIMEOUT = self.stage4_idle_timeout_var.get()
#         settings.STAGE4_COUNTDOWN_DURATION = self.stage4_countdown_var.get()
#         settings.WEB_URL = self.web_url_var.get()
#         settings.FULLSCREEN_MODE = self.fullscreen_var.get()
#         settings.DEBUG_MODE = self.debug_var.get()
    
#     def detect_cameras(self):
#         """Detect cameras"""
#         self.status_indicator.config(text="● DETECTING...", fg=self.colors['warning'])
#         script = os.path.join(os.path.dirname(__file__), "utility", "detect_camera.py")
#         subprocess.run([sys.executable, script])
#         self.status_indicator.config(text="● READY", fg=self.colors['text_dim'])
    
#     def calibrate_distance(self):
#         """Calibrate distance"""
#         self.status_indicator.config(text="● CALIBRATING...", fg=self.colors['warning'])
#         script = os.path.join(os.path.dirname(__file__), "utility", "calibration_tool.py")
#         subprocess.run([sys.executable, script])
#         self.status_indicator.config(text="● READY", fg=self.colors['text_dim'])
    
#     def test_components(self):
#         """Test components"""
#         self.status_indicator.config(text="● TESTING...", fg=self.colors['warning'])
#         script = os.path.join(os.path.dirname(__file__), "utility", "test_components.py")
#         subprocess.run([sys.executable, script])
#         self.status_indicator.config(text="● READY", fg=self.colors['text_dim'])
    
#     def check_media_files(self):
#         """Check media files"""
#         media_files = [
#             "assets/idle-looping.mp4",
#             "assets/hand-waving.webm",
#             "assets/woman-speech.mp3",
#             "assets/thank-you.mp4"
#         ]
        
#         found = [f for f in media_files if Path(f).exists()]
#         missing = [f for f in media_files if not Path(f).exists()]
        
#         msg = "MEDIA FILES CHECK\n\n"
#         if found:
#             msg += "✅ Found:\n" + "\n".join(f"  • {f}" for f in found)
#         if missing:
#             msg += "\n\n❌ Missing:\n" + "\n".join(f"  • {f}" for f in missing)
#         else:
#             msg += "\n\n🎉 All files present!"
        
#         messagebox.showinfo("Media Files", msg)
    
#     def view_logs(self):
#         """View logs"""
#         log_file = "kiosk_activity.log"
#         if Path(log_file).exists():
#             os.system(f"notepad {log_file}" if os.name == 'nt' else f"gedit {log_file}")
#         else:
#             messagebox.showinfo("Logs", "No logs yet. Run kiosk first.")
    
#     def save_settings(self):
#         """Save settings"""
#         self.config["camera_index"] = self.camera_index_var.get()
#         self.config["distance_far"] = self.distance_far_var.get()
#         self.config["distance_near"] = self.distance_near_var.get()
#         self.config["distance_very_near"] = self.distance_very_near_var.get()
#         self.config["stage2_countdown"] = self.stage2_countdown_var.get()
#         self.config["stage3_timeout"] = self.stage3_timeout_var.get()
#         self.config["stage4_idle_timeout"] = self.stage4_idle_timeout_var.get()
#         self.config["stage4_countdown"] = self.stage4_countdown_var.get()
#         self.config["web_url"] = self.web_url_var.get()
#         self.config["fullscreen"] = self.fullscreen_var.get()
#         self.config["debug_mode"] = self.debug_var.get()
        
#         self.save_config()
        
#         # Visual feedback
#         self.status_indicator.config(text="● SAVED", fg=self.colors['success'])
#         self.root.after(2000, lambda: self.status_indicator.config(
#             text="● READY", fg=self.colors['text_dim']
#         ))
    
#     def run(self):
#         """Start GUI"""
#         self.root.mainloop()


# if __name__ == "__main__":
#     app = ModernKioskGUI()
#     app.run()