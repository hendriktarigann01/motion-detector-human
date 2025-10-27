"""
Component Test Script
Tests all components before running main application
"""

import sys
from pathlib import Path
import cv2

sys.path.append(str(Path(__file__).parent))
from config import settings as config

print("="*70)
print(" MJ SOLUTION KIOSK - COMPONENT TEST")
print("="*70)
print()

# Test results
tests_passed = 0
tests_failed = 0
warnings = []


def test_result(name, passed, message=""):
    """Print test result"""
    global tests_passed, tests_failed
    
    if passed:
        print(f"✅ {name}: PASSED")
        tests_passed += 1
    else:
        print(f"❌ {name}: FAILED")
        if message:
            print(f"   → {message}")
        tests_failed += 1
    print()


print("🔍 Running component tests...\n")

# ============================================================
# TEST 1: Python Packages
# ============================================================
print("📦 Test 1: Checking Python packages...")

try:
    import cv2
    test_result("OpenCV (cv2)", True)
except ImportError as e:
    test_result("OpenCV (cv2)", False, f"pip install opencv-python")

try:
    import torch
    test_result("PyTorch", True)
except ImportError:
    test_result("PyTorch", False, "pip install torch torchvision")

try:
    import pygame
    test_result("Pygame", True)
except ImportError:
    test_result("Pygame", False, "pip install pygame")

try:
    import pyautogui
    test_result("PyAutoGUI", True)
except ImportError:
    test_result("PyAutoGUI", False, "pip install pyautogui")

try:
    import numpy as np
    test_result("NumPy", True)
except ImportError:
    test_result("NumPy", False, "pip install numpy")


# ============================================================
# TEST 2: Config File
# ============================================================
print("⚙️  Test 2: Checking configuration...")

try:
    from config import settings
    test_result("Config file", True)
    
    # Check critical settings
    if hasattr(config, 'CAMERA_INDEX'):
        print(f"   Camera Index: {config.CAMERA_INDEX}")
    if hasattr(config, 'YOLO_MODEL_PATH'):
        print(f"   YOLO Model: {config.YOLO_MODEL_PATH}")
    print()
    
except ImportError as e:
    test_result("Config file", False, str(e))


# ============================================================
# TEST 3: Camera
# ============================================================
print("📹 Test 3: Checking camera...")

try:
    from helpers.camera_helper import initialize_camera
    camera = initialize_camera(config.CAMERA_INDEX, 640, 480)
    
    ret, frame = camera.read()
    if ret and frame is not None:
        test_result("Camera capture", True)
        print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
        print(f"   Channels: {frame.shape[2]}")
    else:
        test_result("Camera capture", False, "Cannot read frame")
    
    camera.release()
    print()
    
except Exception as e:
    test_result("Camera", False, str(e))


# ============================================================
# TEST 4: YOLO Model
# ============================================================
print("🎯 Test 4: Checking YOLO model...")

try:
    from models.yolo_detector import YOLOPersonDetector
    
    print("   Loading YOLO model (this may take a while)...")
    detector = YOLOPersonDetector(config)
    
    test_result("YOLO model", True)
    print(f"   Model: {config.YOLO_MODEL_PATH}")
    print(f"   Device: {config.YOLO_DEVICE}")
    print()
    
except Exception as e:
    test_result("YOLO model", False, str(e))


# ============================================================
# TEST 5: Media Files
# ============================================================
print("🎬 Test 5: Checking media files...")

# Check idle video
idle_path = Path(config.VIDEO_IDLE_LOOP)
if idle_path.exists():
    cap = cv2.VideoCapture(str(idle_path))
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0
        test_result("Idle video", True)
        print(f"   File: {idle_path.name}")
        print(f"   Duration: {duration:.1f}s, FPS: {fps:.1f}")
        cap.release()
    else:
        test_result("Idle video", False, "Cannot open file")
else:
    test_result("Idle video", False, f"File not found: {idle_path}")
    warnings.append("Idle video missing - create assets/idle-looping.mp4")

# Check waving video
waving_path = Path(config.VIDEO_HAND_WAVING)
if waving_path.exists():
    cap = cv2.VideoCapture(str(waving_path))
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0
        test_result("Hand-waving video", True)
        print(f"   File: {waving_path.name}")
        print(f"   Duration: {duration:.1f}s, FPS: {fps:.1f}")
        cap.release()
    else:
        test_result("Hand-waving video", False, "Cannot open file")
else:
    test_result("Hand-waving video", False, f"File not found: {waving_path}")
    warnings.append("Hand-waving video missing - create assets/hand-waving.webm")

# Check audio
audio_path = Path(config.AUDIO_SPEECH)
if audio_path.exists():
    test_result("Speech audio", True)
    print(f"   File: {audio_path.name}")
    print(f"   Size: {audio_path.stat().st_size / 1024:.1f} KB")
    print()
else:
    test_result("Speech audio", False, f"File not found: {audio_path}")
    warnings.append("Speech audio missing - create assets/woman-speech.mp3")


# ============================================================
# TEST 6: State Machine
# ============================================================
print("🔄 Test 6: Checking state machine...")

try:
    from models.state_machine import StateMachine, KioskState
    
    sm = StateMachine(config)
    
    # Test initial state
    if sm.current_state == KioskState.STAGE_1_IDLE:
        test_result("State Machine init", True)
    else:
        test_result("State Machine init", False, "Wrong initial state")
    
    # Test transition
    sm.update(person_detected=True, distance_status='near')
    if sm.current_state == KioskState.STAGE_2_DETECTED:
        print("   ✅ State transition working")
    else:
        warnings.append("State transition may have issues")
    
    print()
    
except Exception as e:
    test_result("State Machine", False, str(e))


# ============================================================
# TEST 7: Media Player
# ============================================================
print("🎵 Test 7: Checking media player...")

try:
    from helpers.media_player import MediaPlayer
    import pygame
    
    player = MediaPlayer(config)
    test_result("Media Player init", True)
    
    # Test video loading
    if player.idle_video and player.idle_video.isOpened():
        print("   ✅ Idle video loaded")
    else:
        warnings.append("Idle video not loaded properly")
    
    if player.waving_video and player.waving_video.isOpened():
        print("   ✅ Waving video loaded")
    else:
        warnings.append("Waving video not loaded properly")
    
    player.cleanup()
    print()
    
except Exception as e:
    test_result("Media Player", False, str(e))


# ============================================================
# TEST 8: Web Interface Handler
# ============================================================
print("🌐 Test 8: Checking web interface handler...")

try:
    from helpers.web_interface import WebInterfaceHandler
    
    web = WebInterfaceHandler(config)
    test_result("Web Interface Handler", True)
    print(f"   URL: {config.WEB_URL}")
    print(f"   Fullscreen: {config.FULLSCREEN_MODE}")
    print()
    
except Exception as e:
    test_result("Web Interface Handler", False, str(e))


# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print(" TEST SUMMARY")
print("="*70)
print()
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
print()

if warnings:
    print("⚠️  WARNINGS:")
    for warning in warnings:
        print(f"   • {warning}")
    print()

if tests_failed == 0:
    print("🎉 ALL TESTS PASSED!")
    print()
    print("✅ System ready to run. Next steps:")
    print("   1. Run calibration: python calibration_tool.py")
    print("   2. Run application: python main_refactored.py")
    print()
else:
    print("❌ SOME TESTS FAILED!")
    print()
    print("📝 Action items:")
    print("   1. Install missing packages: pip install -r requirements.txt")
    print("   2. Check camera connection")
    print("   3. Add media files to assets/ folder")
    print("   4. Fix configuration issues")
    print()

print("="*70)