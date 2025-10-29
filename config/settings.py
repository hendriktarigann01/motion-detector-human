# Configuration file for Kiosk Motion Detection System

# ==================== CAMERA SETTINGS ====================
CAMERA_INDEX = 1  # 0 for laptop, change for external camera
# DEVELOPMENT MODE (Manual Switch)
DEVELOPMENT_MODE = True  # Set to False for production

if DEVELOPMENT_MODE:
    CAMERA_WIDTH = 360   # Development: Portrait 9:16
    CAMERA_HEIGHT = 640
else:
    CAMERA_WIDTH = 1080  # Production: Portrait 9:16
    CAMERA_HEIGHT = 1920

FPS_SMOOTHING_INTERVAL = 2

# ==================== YOLO SETTINGS ====================
YOLO_MODEL_PATH = "yolov5s.pt"  # Will auto-download if not exists
YOLO_CONFIDENCE = 0.5
YOLO_DEVICE = "cpu"  # Change to "cuda" if GPU available

# ==================== DISTANCE THRESHOLDS ====================
# Based on bounding box height (pixels)
# CALIBRATE THESE VALUES based on your camera setup!
DISTANCE_FAR = 150      # >5m: bbox height < 150px 
DISTANCE_NEAR = 300     # ~3m: bbox height 150-450px 
DISTANCE_VERY_NEAR = 450  # ≤0.6m: bbox height >= 700px

# ==================== STAGE TIMEOUTS ====================
STAGE2_COUNTDOWN = 10  # seconds (when person leaves)
STAGE3_RESPONSE_TIMEOUT = 15  # seconds for user response
STAGE4_IDLE_TIMEOUT = 15  # seconds idle before countdown
STAGE4_COUNTDOWN_DURATION = 60  # final countdown before reset

# ==================== MEDIA PATHS ====================
# Stage 1: Welcome Animation (Idle)
WELCOME_ANIMATION = "assets/welcome-animation.mp4"

# Stage 2 & 3: Hand Waving Video + Audio (play together, looping)
VIDEO_HAND_WAVING = "assets/hand-waving.mp4"
AUDIO_HAND_WAVING = "assets/hand-waving.mp3"

# ==================== WEB INTERFACE ====================
WEB_URL = "http://localhost:5173/"

# ==================== INTERACTION DETECTION ====================
MOUSE_IDLE_THRESHOLD = 5  # seconds without mouse movement = idle
TOUCH_IDLE_THRESHOLD = 5  # seconds without touch = idle

# ==================== VIDEO SETTINGS ====================
VIDEO_FPS = 30  # Cap video FPS for smoother playback
VIDEO_BUFFER_SIZE = 3  # Buffer frames

# ==================== TRANSITION SETTINGS ====================
FADE_DURATION = 1.0  # Fade transition duration in seconds (black)
FADE_COLOR = (0, 0, 0)  # Black fade

# ==================== BUTTON SETTINGS ====================
BUTTON_PADDING = 20  # Padding from screen edges
BUTTON_WIDTH = 200  # Button width
BUTTON_HEIGHT = 60  # Button height
BUTTON_COLOR = (50, 150, 255)  # Blue button
BUTTON_HOVER_COLOR = (80, 180, 255)  # Lighter blue on hover
BUTTON_TEXT_COLOR = (255, 255, 255)  # White text
BUTTON_FONT_SCALE = 0.7
BUTTON_FONT_THICKNESS = 2

# ==================== DEBUG SETTINGS ====================
DEBUG_MODE = True  # Show bounding boxes and distance info
SHOW_FPS = True
SAVE_LOGS = True
LOG_FILE = "kiosk_activity.log"

# ==================== DISPLAY SETTINGS ====================
FULLSCREEN_MODE = False  # False for development/testing
WINDOW_NAME = "MJ Solution Kiosk"