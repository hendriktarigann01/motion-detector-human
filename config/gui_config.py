"""
Configuration Data for C-Merch Kiosk Dashboard
Separated data from code for clean architecture
"""

from pathlib import Path

# ==================== COLORS ====================
# Modern Light Theme
BG_MAIN = "#f5f5f5"
BG_WHITE = "#ffffff"
HEADER_BG = "#ffffff"
BORDER_COLOR = "#e0e0e0"
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#666666"
TEXT_MUTED = "#999999"

# Button Colors
BTN_CALIBRATION = "#3d3d8f"  # Dark blue/purple
BTN_START = "#7ed321"        # Bright green
BTN_TEST = "#f5a623"         # Orange
BTN_RESET = "#e74c3c"        # Red
BTN_EDIT = "#95a5a6"         # Gray


# ==================== PATHS ====================
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "c-merch-color.png"
ICON_PATH = BASE_DIR / "assets" / "icon-c-merch-color.ico"
CONFIG_PATH = BASE_DIR / "config" / "data" / "settings.json"
SETTINGS_PATH = BASE_DIR / "settings.py"

# Scripts
MAIN_APP = BASE_DIR / "main.py"
CALIBRATION_TOOL = BASE_DIR / "utility" / "calibration_tool.py"
TEST_COMPONENTS = BASE_DIR / "utility" / "test_components.py"

# Icon directory
ICON_DIR = BASE_DIR / "assets" / "icons"


# ==================== LABELS (Indonesian) ====================
CONFIG_LABELS = {
    "camera_index": "Kamera yang Digunakan",
    "distance_far": "Jarak Orang Terjauh",
    "distance_near": "Jarak Orang Menengah",
    "distance_very_near": "Jarak Orang Dekat",
    "stage2_countdown": "Waktu Tunggu Orang Terlalu Jauh",
    "stage3_timeout": "Waktu Tunggu Saat Orang Pergi",
    "stage4_idle_timeout": "Waktu Tunggu Tombol Diklik",
    "stage4_countdown": "Waktu Diam di Halaman Web",
    "web_url": "URL Web",
    "fullscreen": "Mode Fullscreen",
    "debug_mode": "Mode Debug"
}


# ==================== DESCRIPTIONS (Indonesian) ====================
CONFIG_DESCRIPTIONS = {
    "camera_index": 'Pilih kamera mana yang ingin dipakai: "0" untuk kamera bawaan laptop, "1" untuk kamera eksternal.',
    "distance_far": "Batas sistem mengenali orang yang masih jauh dari layar",
    "distance_near": "Batas sistem mengenali orang yang mulai mendekat ke layar => audio pun mulai terdengar.",
    "distance_very_near": "Batas sistem mengenali orang yang sudah di depan layar => pelanggan akan di arahkan ke halaman catalog",
    "stage2_countdown": "Jika orang sudah terlihat tapi tetap jauh selama waktu ini, sistem akan kembali ke tampilan awal.",
    "stage3_timeout": "Jika orang yang terdeteksi pergi dan tidak kembali dalam waktu ini, sistem kembali ke tampilan awal.",
    "stage4_idle_timeout": "Setelah video dan suara muncul, sistem menunggu tombol ditekan dalam waktu ini. Kalau tidak ditekan, sistem kembali ke awal.",
    "stage4_countdown": "Jika tidak ada aktivitas di halaman web selama waktu ini, sistem akan mulai menghitung mundur untuk kembali ke tampilan awal.",
    "web_url": "URL website yang akan ditampilkan",
    "fullscreen": "Mode layar penuh",
    "debug_mode": "Mode debug untuk development"
}


# ==================== DEFAULT CONFIG VALUES ====================
DEFAULT_CONFIG = {
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


# ==================== SETTINGS.PY MAPPING ====================
# Mapping from config keys to settings.py attribute names
SETTINGS_MAPPING = {
    "camera_index": "CAMERA_INDEX",
    "distance_far": "DISTANCE_FAR",
    "distance_near": "DISTANCE_NEAR",
    "distance_very_near": "DISTANCE_VERY_NEAR",
    "stage2_countdown": "STAGE2_COUNTDOWN",
    "stage3_timeout": "STAGE3_RESPONSE_TIMEOUT",
    "stage4_idle_timeout": "STAGE4_IDLE_TIMEOUT",
    "stage4_countdown": "STAGE4_COUNTDOWN_DURATION",
    "web_url": "WEB_URL",
    "fullscreen": "FULLSCREEN_MODE",
    "debug_mode": "DEBUG_MODE"
}