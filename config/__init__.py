"""
Config Package Initializer
Auto-loads configuration from settings.json with fallback to settings.py

Priority:
1. config/data/settings.json (runtime config, editable from GUI)
2. config/settings.py (default config, hardcoded)

This allows main.py to use: from config import settings
without any code changes!
"""

import json
import sys
from pathlib import Path

# Get paths
CONFIG_DIR = Path(__file__).parent
JSON_CONFIG_PATH = CONFIG_DIR / "data" / "settings.json"
PY_CONFIG_PATH = CONFIG_DIR / "settings.py"

# Add config dir to path for importing
if str(CONFIG_DIR) not in sys.path:
    sys.path.insert(0, str(CONFIG_DIR))


def load_config_from_json():
    """Load configuration from JSON file"""
    try:
        with open(JSON_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {JSON_CONFIG_PATH}: {e}")
        return None


def create_config_object(json_data, default_settings):
    """
    Create dynamic config object
    Merges JSON data with default settings
    """
    
    class DynamicConfig:
        """Dynamic configuration object"""
        pass
    
    config = DynamicConfig()
    
    # Load from JSON (runtime config)
    if json_data:
        config.CAMERA_INDEX = json_data.get("camera_index", 0)
        config.DISTANCE_FAR = json_data.get("distance_far", 150)
        config.DISTANCE_NEAR = json_data.get("distance_near", 300)
        config.DISTANCE_VERY_NEAR = json_data.get("distance_very_near", 450)
        config.STAGE2_COUNTDOWN = json_data.get("stage2_countdown", 10)
        config.STAGE3_RESPONSE_TIMEOUT = json_data.get("stage3_timeout", 15)
        config.STAGE4_IDLE_TIMEOUT = json_data.get("stage4_idle_timeout", 15)
        config.STAGE4_COUNTDOWN_DURATION = json_data.get("stage4_countdown", 5)
        config.WEB_URL = json_data.get("web_url", "http://localhost:5173/")
        config.FULLSCREEN_MODE = json_data.get("fullscreen", False)
        config.DEBUG_MODE = json_data.get("debug_mode", True)
    
    # Load all other attributes from default settings.py
    if default_settings:
        for attr in dir(default_settings):
            if not attr.startswith('_'):  # Skip private attributes
                # Only set if not already set from JSON
                if not hasattr(config, attr):
                    setattr(config, attr, getattr(default_settings, attr))
                    
        # Override JSON values if they were loaded
        if json_data:
            config.CAMERA_INDEX = json_data.get("camera_index", config.CAMERA_INDEX)
            config.DISTANCE_FAR = json_data.get("distance_far", config.DISTANCE_FAR)
            config.DISTANCE_NEAR = json_data.get("distance_near", config.DISTANCE_NEAR)
            config.DISTANCE_VERY_NEAR = json_data.get("distance_very_near", config.DISTANCE_VERY_NEAR)
            config.STAGE2_COUNTDOWN = json_data.get("stage2_countdown", config.STAGE2_COUNTDOWN)
            config.STAGE3_RESPONSE_TIMEOUT = json_data.get("stage3_timeout", config.STAGE3_RESPONSE_TIMEOUT)
            config.STAGE4_IDLE_TIMEOUT = json_data.get("stage4_idle_timeout", config.STAGE4_IDLE_TIMEOUT)
            config.STAGE4_COUNTDOWN_DURATION = json_data.get("stage4_countdown", config.STAGE4_COUNTDOWN_DURATION)
            config.WEB_URL = json_data.get("web_url", config.WEB_URL)
            config.FULLSCREEN_MODE = json_data.get("fullscreen", config.FULLSCREEN_MODE)
            config.DEBUG_MODE = json_data.get("debug_mode", config.DEBUG_MODE)
    
    return config


# Load default settings from settings.py
try:
    import settings as default_settings
    print(f"✓ Loaded default settings from: {PY_CONFIG_PATH}")
except ImportError as e:
    print(f"✗ Could not import config/settings.py: {e}")
    default_settings = None

# Try to load JSON config
json_data = load_config_from_json()
if json_data:
    print(f"✓ Loaded runtime config from: {JSON_CONFIG_PATH}")
    print(f"  → Using JSON values for configurable parameters")
else:
    print(f"ℹ No JSON config found, using defaults from settings.py")

# Create merged config object
settings = create_config_object(json_data, default_settings)

# Export
__all__ = ['settings']


# Debug info (only shown once on import)
if __name__ != "__main__":
    import sys
    if hasattr(settings, 'DEVELOPMENT_MODE') and settings.DEVELOPMENT_MODE:
        print(f"\n{'='*60}")
        print(f"CONFIG LOADED:")
        print(f"  Camera: {getattr(settings, 'CAMERA_INDEX', 'N/A')}")
        print(f"  Distances: {getattr(settings, 'DISTANCE_FAR', 'N/A')} / "
              f"{getattr(settings, 'DISTANCE_NEAR', 'N/A')} / "
              f"{getattr(settings, 'DISTANCE_VERY_NEAR', 'N/A')}")
        print(f"  Web URL: {getattr(settings, 'WEB_URL', 'N/A')}")
        print(f"{'='*60}\n")