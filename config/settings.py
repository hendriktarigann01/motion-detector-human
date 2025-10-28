# Configuration file for Kiosk Motion Detection System

# ==================== CAMERA SETTINGS ====================
CAMERA_INDEX = 1  # 0 for laptop, change for external camera
CAMERA_WIDTH = 1280  # FIXED: Reduced for better performance
CAMERA_HEIGHT = 720   # FIXED: Reduced for better performance
FPS_SMOOTHING_INTERVAL = 2

# ==================== YOLO SETTINGS ====================
YOLO_MODEL_PATH = "yolov5s.pt"  # Will auto-download if not exists
YOLO_CONFIDENCE = 0.5
YOLO_DEVICE = "cpu"  # Change to "cuda" if GPU available

# ==================== DISTANCE THRESHOLDS ====================
# Based on bounding box height (pixels)
# CALIBRATE THESE VALUES based on your camera setup!
DISTANCE_FAR = 150      # >5m: bbox height < 150px 
DISTANCE_NEAR = 450     # ~3m: bbox height 150-300px 
DISTANCE_VERY_NEAR = 700  # FIXED: Lowered from 500 to 400 (≤0.6m)

# ==================== STAGE TIMEOUTS ====================
STAGE2_COUNTDOWN = 10  # seconds (5-10s range)
STAGE3_RESPONSE_TIMEOUT = 15  # seconds for user response
STAGE4_IDLE_TIMEOUT = 15  # seconds idle before countdown
STAGE4_COUNTDOWN_DURATION = 60  # final countdown before reset

# ==================== MEDIA PATHS ====================
VIDEO_IDLE_LOOP = "assets/idle-looping.mp4"
VIDEO_HAND_WAVING = "assets/hand-waving.webm"
AUDIO_SPEECH = "assets/woman-speech.mp3"
VIDEO_THANK_YOU = "assets/thank-you.mp4"
AUDIO_THANK_YOU = "assets/thank-you.mp3"  # FIXED: Separate audio file for thank you

# ==================== WEB INTERFACE ====================
WEB_URL = "http://localhost:5173/test"
# WEB_URL = "https://mjsolution.co.id/our-product/"  # Production

# ==================== INTERACTION DETECTION ====================
MOUSE_IDLE_THRESHOLD = 5  # seconds without mouse movement = idle
TOUCH_IDLE_THRESHOLD = 5  # seconds without touch = idle

# ==================== VIDEO SETTINGS ====================
VIDEO_FPS = 30  # FIXED: Cap video FPS for smoother playback
VIDEO_BUFFER_SIZE = 3  # FIXED: Buffer frames

# ==================== DEBUG SETTINGS ====================
DEBUG_MODE = True  # Show bounding boxes and distance info
SHOW_FPS = True
SAVE_LOGS = True
LOG_FILE = "kiosk_activity.log"

# ==================== DISPLAY SETTINGS ====================
FULLSCREEN_MODE = False  # FIXED: False for development/testing
WINDOW_NAME = "MJ Solution Kiosk"