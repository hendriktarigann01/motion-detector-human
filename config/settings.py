"""
Configuration file for MJ Solution Kiosk
Clean and organized settings
"""

# ==================== DEVELOPMENT MODE ====================
DEVELOPMENT_MODE = True # Set to False for production

# ==================== CAMERA SETTINGS ====================
CAMERA_INDEX = 0  # 0 for laptop webcam, 1+ for external camera

# Resolution: Portrait 9:16 aspect ratio
if DEVELOPMENT_MODE:
    CAMERA_WIDTH = 540
    CAMERA_HEIGHT = 960
else:
    CAMERA_WIDTH = 1080
    CAMERA_HEIGHT = 1920

FPS_SMOOTHING_INTERVAL = 2

# ==================== YOLO PERSON DETECTION ====================
YOLO_MODEL_PATH = "yolov5n.pt"  # Auto-download if not exists
YOLO_CONFIDENCE = 0.5
YOLO_DEVICE = "cuda"  # Use "cuda" if GPU available

# ==================== DISTANCE THRESHOLDS ====================

# # For Development (Smaller resolution):
DISTANCE_FAR = 150           # FAR (>5m away)
DISTANCE_NEAR = 300          # NEAR (~3m away)
DISTANCE_VERY_NEAR = 450     # VERY NEAR (<1m away)

# For Production (Normal resolution):
# DISTANCE_FAR = 300           # FAR (>5m away)
# DISTANCE_NEAR = 500          # NEAR (~3m away)
# DISTANCE_VERY_NEAR = 700     # VERY NEAR (<1m away)

# ==================== STATE MACHINE TIMEOUTS ====================
# Stage 2: Person detected
STAGE2_FAR_TIMEOUT = 3       # Return to Stage 1 if person stays FAR
STAGE2_COUNTDOWN = 10        # Return to Stage 1 if person leaves

# Stage 3: Audio playing, waiting for button click
STAGE3_RESPONSE_TIMEOUT = 15 # Return to Stage 1 if no button click

# Stage 4: Web interface active
STAGE4_IDLE_TIMEOUT = 15     # Start countdown if idle
STAGE4_COUNTDOWN_DURATION = 60  # Return to Stage 1 after countdown

# ==================== MEDIA FILES ====================
# Stage 1: Welcome animation (looping)
WELCOME_ANIMATION = "assets/welcome-animation.mp4"

# Stage 2 & 3: Hand waving (video + audio, looping)
VIDEO_HAND_WAVING = "assets/hand-waving.mp4"
AUDIO_HAND_WAVING = "assets/hand-waving.mp3"

# ==================== WEB INTERFACE ====================
WEB_URL = "http://localhost:5173/"

# Idle detection thresholds
MOUSE_IDLE_THRESHOLD = 5     # Seconds without mouse = idle
TOUCH_IDLE_THRESHOLD = 5     # Seconds without touch = idle

# ==================== VIDEO PLAYBACK ====================
VIDEO_FPS = 30               # Target FPS for video playback
VIDEO_BUFFER_SIZE = 3        # Frame buffer size

# ==================== TRANSITIONS ====================
FADE_DURATION = 0.5          # Fade to black duration (seconds)
FADE_COLOR = (0, 0, 0)       # Black

# ==================== BUTTON SETTINGS ====================
# "More Information" button (Stage 3 only, bottom-right)
BUTTON_PADDING = 30          # Distance from screen edges
BUTTON_WIDTH = 250           # Button width
BUTTON_HEIGHT = 70           # Button height

# Colors (BGR format) - DEBUG: Bright colors for visibility
BUTTON_COLOR = (0, 0, 255)           # Bright red background
BUTTON_HOVER_COLOR = (0, 255, 255)   # Yellow on hover
BUTTON_TEXT_COLOR = (255, 255, 255)  # White text

# Text styling
BUTTON_FONT_SCALE = 0.8
BUTTON_FONT_THICKNESS = 2

# ==================== DEBUG & DISPLAY ====================
DEBUG_MODE = True            # Show bounding boxes, timers, etc.
SHOW_FPS = True              # Show FPS counter
SAVE_LOGS = True             # Save logs to file
LOG_FILE = "kiosk_activity.log"

FULLSCREEN_MODE = False      # Use fullscreen (recommended for production)
WINDOW_NAME = "MJ Solution Kiosk"