"""
Component Test Script
Tests all components before running main application
"""
import os
import sys
from pathlib import Path
import cv2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*70)
print("C-Merch KIOSK - COMPONENT TEST")
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
        print(f" {name}: PASSED")
        tests_passed += 1
    else:
        print(f"✗ {name}: FAILED")
        if message:
            print(f"   → {message}")
        tests_failed += 1
    print()


print("Running component tests...\n")

# ============================================================
# TEST 1: Python Packages
# ============================================================
print("Test 1: Checking Python packages...")

try:
    import cv2
    test_result("OpenCV (cv2)", True)
except ImportError as e:
    test_result("OpenCV (cv2)", False, "pip install opencv-python")

try:
    import torch
    test_result("PyTorch", True)
except ImportError:
    test_result("PyTorch", False, "pip install torch torchvision")

try:
    from ultralytics import YOLO
    test_result("Ultralytics YOLO", True)
except ImportError:
    test_result("Ultralytics YOLO", False, "pip install ultralytics")

try:
    import pygame
    test_result("Pygame", True)
except ImportError:
    test_result("Pygame", False, "pip install pygame")

try:
    import numpy as np
    test_result("NumPy", True)
except ImportError:
    test_result("NumPy", False, "pip install numpy")

try:
    from selenium import webdriver
    test_result("Selenium", True)
except ImportError:
    test_result("Selenium", False, "pip install selenium")
    warnings.append("Selenium missing - web interface will be disabled")


# ============================================================
# TEST 2: Settings File
# ============================================================
print("Test 2: Checking settings...")

try:
    from config import settings
    test_result("Settings file", True)
    
    # Check critical settings
    print(f"Development Mode: {settings.DEVELOPMENT_MODE}")
    print(f"Camera Index: {settings.CAMERA_INDEX}")
    print(f"Resolution: {settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT}")
    print(f"YOLO Model: {settings.YOLO_MODEL_PATH}")
    print(f"YOLO Device: {settings.YOLO_DEVICE}")
    print()
    
    # Check distance thresholds
    print(f"Distance Thresholds:")
    print(f"FAR: {settings.DISTANCE_FAR}px")
    print(f"NEAR: {settings.DISTANCE_NEAR}px")
    print(f"VERY NEAR: {settings.DISTANCE_VERY_NEAR}px")
    print()
    
except ImportError as e:
    test_result("Settings file", False, str(e))


# ============================================================
# TEST 3: Camera Helper
# ============================================================
print("Test 3: Checking camera...")

try:
    from helpers.camera_helper import initialize_camera
    from config import settings
    
    camera = initialize_camera(
        settings.CAMERA_INDEX, 
        settings.CAMERA_WIDTH, 
        settings.CAMERA_HEIGHT
    )
    
    ret, frame = camera.read()
    if ret and frame is not None:
        test_result("Camera capture", True)
        print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
        print(f"Channels: {frame.shape[2]}")
    else:
        test_result("Camera capture", False, "Cannot read frame")
    
    camera.release()
    print()
    
except Exception as e:
    test_result("Camera", False, str(e))


# ============================================================
# TEST 4: YOLO Detector
# ============================================================
print("Test 4: Checking YOLO detector...")

try:
    from models.yolo_detector import YOLOPersonDetector
    from config import settings
    
    print("Loading YOLO model (this may take a while)...")
    detector = YOLOPersonDetector(settings)
    
    test_result("YOLO detector", True)
    print(f"Model: {settings.YOLO_MODEL_PATH}")
    print(f"Device: {settings.YOLO_DEVICE}")
    print(f"Confidence: {settings.YOLO_CONFIDENCE}")
    print()
    
except Exception as e:
    test_result("YOLO detector", False, str(e))


# ============================================================
# TEST 5: State Machine
# ============================================================
print("Test 5: Checking state machine...")

try:
    from models.state_machine import StateMachine, KioskState
    from config import settings
    
    sm = StateMachine(settings)
    
    # Test initial state
    if sm.current_state == KioskState.STAGE_1_IDLE:
        test_result("State Machine init", True)
        print(f"Initial state: {sm.current_state.value}")
    else:
        test_result("State Machine init", False, "Wrong initial state")
    
    # Test transition to Stage 2
    sm.update(person_detected=True, distance_status='near')
    if sm.current_state == KioskState.STAGE_2_DETECTED:
        print("Transition to STAGE_2_DETECTED working")
    else:
        warnings.append("State transition to Stage 2 may have issues")
    
    # Test transition to Stage 3
    sm.update(person_detected=True, distance_status='very_near')
    if sm.current_state == KioskState.STAGE_3_AUDIO:
        print("Transition to STAGE_3_AUDIO working")
    else:
        warnings.append("State transition to Stage 3 may have issues")
    
    # Test button click to Stage 4
    sm.update(person_detected=True, distance_status='very_near', button_clicked=True)
    if sm.current_state == KioskState.STAGE_4_WEB:
        print("Transition to STAGE_4_WEB working")
    else:
        warnings.append("State transition to Stage 4 may have issues")
    
    print()
    
except Exception as e:
    test_result("State Machine", False, str(e))


# ============================================================
# TEST 6: Media Files
# ============================================================
print("Test 6: Checking media files...")

from config import settings

# Check welcome animation (Stage 1)
welcome_path = Path(settings.WELCOME_ANIMATION)
if welcome_path.exists():
    cap = cv2.VideoCapture(str(welcome_path))
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0
        test_result("Welcome animation", True)
        print(f"File: {welcome_path.name}")
        print(f"Duration: {duration:.1f}s, FPS: {fps:.1f}")
        cap.release()
    else:
        test_result("Welcome animation", False, "Cannot open file")
else:
    test_result("Welcome animation", False, f"File not found: {welcome_path}")
    warnings.append(f"Welcome animation missing - create {settings.WELCOME_ANIMATION}")

# Check hand-waving video (Stage 2 & 3)
handwaving_path = Path(settings.VIDEO_HAND_WAVING)
if handwaving_path.exists():
    cap = cv2.VideoCapture(str(handwaving_path))
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frames / fps if fps > 0 else 0
        test_result("Hand-waving video", True)
        print(f"File: {handwaving_path.name}")
        print(f"Duration: {duration:.1f}s, FPS: {fps:.1f}")
        cap.release()
    else:
        test_result("Hand-waving video", False, "Cannot open file")
else:
    test_result("Hand-waving video", False, f"File not found: {handwaving_path}")
    warnings.append(f"Hand-waving video missing - create {settings.VIDEO_HAND_WAVING}")

# Check hand-waving audio (Stage 2 & 3)
audio_path = Path(settings.AUDIO_HAND_WAVING)
if audio_path.exists():
    test_result("Hand-waving audio", True)
    print(f"File: {audio_path.name}")
    print(f"Size: {audio_path.stat().st_size / 1024:.1f} KB")
    print()
else:
    test_result("Hand-waving audio", False, f"File not found: {audio_path}")
    warnings.append(f"Hand-waving audio missing - create {settings.AUDIO_HAND_WAVING}")


# ============================================================
# TEST 7: Media Player
# ============================================================
print("Test 7: Checking media player...")

try:
    from helpers.media_player import MediaPlayer
    import pygame
    from config import settings
    
    player = MediaPlayer(settings)
    test_result("Media Player init", True)
    
    # Test video loading
    if player.welcome_video and player.welcome_video.isOpened():
        print("Welcome animation loaded")
    else:
        warnings.append("Welcome animation not loaded properly")
    
    if player.handwaving_video and player.handwaving_video.isOpened():
        print("Hand-waving video loaded")
    else:
        warnings.append("Hand-waving video not loaded properly")
    
    # Test pygame mixer
    try:
        pygame.mixer.get_init()
        print("Pygame mixer initialized")
    except:
        warnings.append("Pygame mixer not initialized properly")
    
    player.cleanup()
    print()
    
except Exception as e:
    test_result("Media Player", False, str(e))


# ============================================================
# TEST 8: Web Interface Handler
# ============================================================
print("Test 8: Checking web interface handler...")

try:
    from helpers.web_interface import WebInterfaceHandler
    from config import settings
    
    web = WebInterfaceHandler(settings)
    test_result("Web Interface Handler", True)
    print(f"URL: {settings.WEB_URL}")
    print(f"Development Mode: {settings.DEVELOPMENT_MODE}")
    
    # Check if Selenium is available
    from helpers.web_interface import SELENIUM_AVAILABLE
    if SELENIUM_AVAILABLE:
        print("Selenium available")
    else:
        warnings.append("Selenium not available - web interface will use fallback")
    
    print()
    
except Exception as e:
    test_result("Web Interface Handler", False, str(e))


# ============================================================
# TEST 9: Integration Test (Optional)
# ============================================================
print("Test 9: Quick integration test...")

try:
    from helpers.camera_helper import initialize_camera
    from models.yolo_detector import YOLOPersonDetector
    from models.state_machine import StateMachine
    from helpers.media_player import MediaPlayer
    from config import settings
    
    # Initialize components
    camera = initialize_camera(settings.CAMERA_INDEX, settings.CAMERA_WIDTH, settings.CAMERA_HEIGHT)
    detector = YOLOPersonDetector(settings)
    state_machine = StateMachine(settings)
    media_player = MediaPlayer(settings)
    
    # Test one frame
    ret, frame = camera.read()
    if ret:
        person_detected, bbox, distance_status, confidence = detector.detect_person(frame)
        state_machine.update(person_detected, distance_status or 'far')
        video_frame = media_player.get_video_frame()
        
        test_result("Integration test", True)
        print(f"Person detected: {person_detected}")
        if person_detected:
            print(f"Distance: {distance_status}")
            print(f"Confidence: {confidence:.2f}")
        print(f"State: {state_machine.current_state.value}")
    else:
        test_result("Integration test", False, "Cannot read camera frame")
    
    # Cleanup
    camera.release()
    media_player.cleanup()
    print()
    
except Exception as e:
    test_result("Integration test", False, str(e))


# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print(" TEST SUMMARY")
print("="*70)
print()
print(f" Passed: {tests_passed}")
print(f"✗ Failed: {tests_failed}")
print()

if warnings:
    print(" WARNINGS:")
    for warning in warnings:
        print(f"   • {warning}")
    print()

if tests_failed == 0:
    print("ALL TESTS PASSED!")
    print(" System ready to run")
    print()
    print("Next steps:")
    print("1. Run: python main.py")
    print("2. Make sure web server is running at", settings.WEB_URL if 'settings' in dir() else "http://localhost:5173/")
    print()
else:
    print("SOME TESTS FAILED!")
    print()
    print("Action items:")
    print("1. Install missing packages: pip install -r requirements.txt")
    print("2. Check camera connection")
    print("3. Add media files to assets/ folder:")
    print(f"{settings.WELCOME_ANIMATION if 'settings' in dir() else 'assets/welcome-animation.mp4'}")
    print(f"{settings.VIDEO_HAND_WAVING if 'settings' in dir() else 'assets/hand-waving.mp4'}")
    print(f"{settings.AUDIO_HAND_WAVING if 'settings' in dir() else 'assets/hand-waving.mp3'}")
    print("4. Fix configuration issues in settings.py")
    print()

print("="*70)