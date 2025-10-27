# Configuration file for Kiosk Motion Detection System #


# ==================== CAMERA SETTINGS ====================
CAMERA_INDEX = 0  # 0 for laptop, change for external camera
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FPS_SMOOTHING_INTERVAL = 2

# ==================== YOLO SETTINGS ====================
YOLO_MODEL_PATH = "yolov5s.pt"  # Will auto-download if not exists
YOLO_CONFIDENCE = 0.5
YOLO_DEVICE = "cpu"  # Change to "cuda" if GPU available

# ==================== DISTANCE THRESHOLDS ====================
# Based on bounding box height (pixels)
# You need to calibrate these values based on your camera height/angle
DISTANCE_FAR = 150 # >5m: bbox height < 150px 
DISTANCE_NEAR = 300 # <5m: bbox height > 300px 
DISTANCE_VERY_NEAR = 500 # ≤0.6m: bbox height > 500px

# ==================== STAGE TIMEOUTS ====================
STAGE2_COUNTDOWN = 10  # seconds (5-10s range, you can adjust)
STAGE3_RESPONSE_TIMEOUT = 15  # seconds for user response
STAGE4_IDLE_TIMEOUT = 15  # seconds (10-20s range)
STAGE4_COUNTDOWN_DURATION = 5  # final countdown before reset

# ==================== MEDIA PATHS ====================
VIDEO_IDLE_LOOP = "assets/idle-looping.mp4"
VIDEO_HAND_WAVING = "assets/hand-waving.webm"
VIDEO_THANK_YOU = "assets/thank-you.mp4"
AUDIO_SPEECH = "assets/woman-speech.mp3"

# ==================== WEB INTERFACE ====================
WEB_URL = "https://mjsolution.co.id/our-product/"
# WEB_URL = "http://localhost:8000"  # For local testing

# ==================== INTERACTION DETECTION ====================
MOUSE_IDLE_THRESHOLD = 5  # seconds without mouse movement = idle
TOUCH_IDLE_THRESHOLD = 5  # seconds without touch = idle

# ==================== VIDEO TRANSITION ====================
FADE_DURATION = 1.0  # seconds for fade transition

# ==================== DEBUG SETTINGS ====================
DEBUG_MODE = True  # Show bounding boxes and distance info
SHOW_FPS = True
SAVE_LOGS = True
LOG_FILE = "kiosk_activity.log"

# ==================== DISPLAY SETTINGS ====================
FULLSCREEN_MODE = True  # Set False for development
WINDOW_NAME = "MJ Solution Kiosk" 