"""
Config Loader for main.py
Loads from settings.json (runtime config) with fallback to settings.py (defaults)
"""

import json
import sys
from pathlib import Path

# Add config directory to path
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
sys.path.insert(0, str(CONFIG_DIR))

# Import default settings
try:
    import settings as default_settings
except ImportError:
    print("Warning: Could not import config/settings.py")
    default_settings = None


def load_config():
    """
    Load configuration with priority:
    1. config/data/settings.json (runtime, editable from GUI)
    2. config/settings.py (default, hardcoded)
    """
    
    json_path = CONFIG_DIR / "data" / "settings.json"
    
    # Try to load from JSON first
    if json_path.exists():
        try:
            with open(json_path, 'r') as f:
                json_config = json.load(f)
            
            print(f"✓ Loaded config from: {json_path}")
            
            # Create config object with JSON values
            config = ConfigObject(json_config)
            return config
            
        except Exception as e:
            print(f"⚠ Failed to load {json_path}: {e}")
            print("  → Falling back to settings.py")
    
    # Fallback to settings.py
    if default_settings:
        print(f"✓ Using default config from: config/settings.py")
        return default_settings
    else:
        raise Exception("No configuration found! Please check config/settings.py or config/data/settings.json")


class ConfigObject:
    """
    Dynamic config object that loads from JSON
    Maps JSON keys to settings.py attribute names
    """
    
    def __init__(self, json_data):
        # Map JSON to settings.py attributes
        self.CAMERA_INDEX = json_data.get("camera_index", 0)
        self.DISTANCE_FAR = json_data.get("distance_far", 150)
        self.DISTANCE_NEAR = json_data.get("distance_near", 300)
        self.DISTANCE_VERY_NEAR = json_data.get("distance_very_near", 450)
        
        self.STAGE2_COUNTDOWN = json_data.get("stage2_countdown", 10)
        self.STAGE3_RESPONSE_TIMEOUT = json_data.get("stage3_timeout", 15)
        self.STAGE4_IDLE_TIMEOUT = json_data.get("stage4_idle_timeout", 15)
        self.STAGE4_COUNTDOWN_DURATION = json_data.get("stage4_countdown", 5)
        
        self.WEB_URL = json_data.get("web_url", "http://localhost:5173/")
        self.FULLSCREEN_MODE = json_data.get("fullscreen", False)
        self.DEBUG_MODE = json_data.get("debug_mode", True)
        
        # Load other settings from default settings.py if available
        try:
            import settings as defaults
            
            # Development mode
            self.DEVELOPMENT_MODE = getattr(defaults, 'DEVELOPMENT_MODE', True)
            
            # Camera settings
            self.CAMERA_WIDTH = getattr(defaults, 'CAMERA_WIDTH', 540)
            self.CAMERA_HEIGHT = getattr(defaults, 'CAMERA_HEIGHT', 960)
            self.FPS_SMOOTHING_INTERVAL = getattr(defaults, 'FPS_SMOOTHING_INTERVAL', 2)
            
            # YOLO settings
            self.YOLO_MODEL_PATH = getattr(defaults, 'YOLO_MODEL_PATH', "yolov5n.pt")
            self.YOLO_CONFIDENCE = getattr(defaults, 'YOLO_CONFIDENCE', 0.5)
            self.YOLO_DEVICE = getattr(defaults, 'YOLO_DEVICE', "cpu")
            
            # Media files
            self.WELCOME_ANIMATION = getattr(defaults, 'WELCOME_ANIMATION', "assets/welcome-animation.mp4")
            self.VIDEO_HAND_WAVING = getattr(defaults, 'VIDEO_HAND_WAVING', "assets/hand-waving.mp4")
            self.AUDIO_HAND_WAVING = getattr(defaults, 'AUDIO_HAND_WAVING', "assets/hand-waving.mp3")
            
            # Video playback
            self.VIDEO_FPS = getattr(defaults, 'VIDEO_FPS', 30)
            self.VIDEO_BUFFER_SIZE = getattr(defaults, 'VIDEO_BUFFER_SIZE', 3)
            
            # Transitions
            self.FADE_DURATION = getattr(defaults, 'FADE_DURATION', 0.5)
            self.FADE_COLOR = getattr(defaults, 'FADE_COLOR', (0, 0, 0))
            
            # Button settings
            self.BUTTON_PADDING = getattr(defaults, 'BUTTON_PADDING', 8)
            self.BUTTON_WIDTH = getattr(defaults, 'BUTTON_WIDTH', 200)
            self.BUTTON_HEIGHT = getattr(defaults, 'BUTTON_HEIGHT', 40)
            self.BUTTON_COLOR = getattr(defaults, 'BUTTON_COLOR', (113, 34, 37))
            self.BUTTON_HOVER_COLOR = getattr(defaults, 'BUTTON_HOVER_COLOR', (87, 12, 15))
            self.BUTTON_TEXT_COLOR = getattr(defaults, 'BUTTON_TEXT_COLOR', (255, 255, 255))
            self.BUTTON_FONT_SCALE = getattr(defaults, 'BUTTON_FONT_SCALE', 0.6)
            self.BUTTON_FONT_THICKNESS = getattr(defaults, 'BUTTON_FONT_THICKNESS', 1)
            
            # Debug & Display
            self.SHOW_FPS = getattr(defaults, 'SHOW_FPS', True)
            self.SAVE_LOGS = getattr(defaults, 'SAVE_LOGS', True)
            self.LOG_FILE = getattr(defaults, 'LOG_FILE', "kiosk_activity.log")
            self.WINDOW_NAME = getattr(defaults, 'WINDOW_NAME', "C-Merch Kiosk")
            
            # Stage 2 timeouts
            self.STAGE2_FAR_TIMEOUT = getattr(defaults, 'STAGE2_FAR_TIMEOUT', 3)
            
            # Idle detection
            self.MOUSE_IDLE_THRESHOLD = getattr(defaults, 'MOUSE_IDLE_THRESHOLD', 5)
            self.TOUCH_IDLE_THRESHOLD = getattr(defaults, 'TOUCH_IDLE_THRESHOLD', 5)
            
        except ImportError:
            print("Warning: Could not import config/settings.py for additional settings")
    
    def __repr__(self):
        return f"ConfigObject(camera={self.CAMERA_INDEX}, distances=[{self.DISTANCE_FAR}, {self.DISTANCE_NEAR}, {self.DISTANCE_VERY_NEAR}])"


# Export loaded config
config = load_config()
settings = config  # Alias untuk compatibility

# Make both available
__all__ = ['config', 'settings']


if __name__ == "__main__":
    # Test config loader
    print("\n" + "="*60)
    print("CONFIG LOADER TEST")
    print("="*60)
    
    print(f"\nConfig Object: {config}")
    print(f"\nKey Settings:")
    print(f"  Camera Index: {config.CAMERA_INDEX}")
    print(f"  Distance Far: {config.DISTANCE_FAR}")
    print(f"  Distance Near: {config.DISTANCE_NEAR}")
    print(f"  Distance Very Near: {config.DISTANCE_VERY_NEAR}")
    print(f"  Stage 2 Countdown: {config.STAGE2_COUNTDOWN}")
    print(f"  Stage 3 Timeout: {config.STAGE3_RESPONSE_TIMEOUT}")
    print(f"  Stage 4 Idle: {config.STAGE4_IDLE_TIMEOUT}")
    print(f"  Stage 4 Countdown: {config.STAGE4_COUNTDOWN_DURATION}")
    print(f"  Web URL: {config.WEB_URL}")
    print(f"  Fullscreen: {config.FULLSCREEN_MODE}")
    print(f"  Debug Mode: {config.DEBUG_MODE}")
    print("\n" + "="*60)