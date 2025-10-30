"""
Distance Calibration Tool - Enhanced Version
Saves calibration data to config/kiosk_config.json
"""

import cv2
import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings as config
from models.yolo_detector import YOLOPersonDetector
from helpers.camera_helper import initialize_camera

# Paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "kiosk_config.json"

print("="*70)
print("                   DISTANCE CALIBRATION TOOL")
print("="*70)
print()
print("This tool helps you calibrate distance thresholds for your camera setup.")
print()
print("INSTRUCTIONS:")
print("   1. Stand at approximately 5+ meters from camera → Press 'f' (FAR)")
print("   2. Stand at approximately 3 meters from camera  → Press 'n' (NEAR)")
print("   3. Stand at approximately 0.6 meters or closer  → Press 'v' (VERY NEAR)")
print("   4. Repeat steps 1-3 for better accuracy (3-5 measurements each)")
print()
print("CONTROLS:")
print("   - Press 'f' : Save as FAR measurement")
print("   - Press 'n' : Save as NEAR measurement")
print("   - Press 'v' : Save as VERY NEAR measurement")
print("   - Press 's' : Save configuration to file")
print("   - Press 'q' : Quit without saving")
print()
print("="*70)

# Storage for measurements
measurements = {
    'far': [],
    'near': [],
    'very_near': []
}


def load_current_config():
    """Load existing config or create default"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default config
    return {
        "camera_index": config.CAMERA_INDEX,
        "distance_far": config.DISTANCE_FAR,
        "distance_near": config.DISTANCE_NEAR,
        "distance_very_near": config.DISTANCE_VERY_NEAR,
        "stage2_countdown": config.STAGE2_COUNTDOWN,
        "stage3_timeout": config.STAGE3_RESPONSE_TIMEOUT,
        "stage4_idle_timeout": config.STAGE4_IDLE_TIMEOUT,
        "stage4_countdown": config.STAGE4_COUNTDOWN_DURATION,
        "web_url": config.WEB_URL,
        "fullscreen": config.FULLSCREEN_MODE,
        "debug_mode": config.DEBUG_MODE
    }


def save_calibration_config(measurements, current_config):
    """Save calibrated values to JSON"""
    # Calculate recommended thresholds
    new_config = current_config.copy()
    
    if measurements['far']:
        # FAR: Average of far measurements
        avg_far = sum(measurements['far']) / len(measurements['far'])
        new_config['distance_far'] = int(avg_far)
    
    if measurements['near']:
        # NEAR: Average of near measurements
        avg_near = sum(measurements['near']) / len(measurements['near'])
        new_config['distance_near'] = int(avg_near)
    
    if measurements['very_near']:
        # VERY NEAR: Average of very near measurements
        avg_very_near = sum(measurements['very_near']) / len(measurements['very_near'])
        new_config['distance_very_near'] = int(avg_very_near)
    
    # Save to file
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(new_config, f, indent=4)
    
    return new_config


def main():
    current_config = load_current_config()
    
    try:
        # Initialize
        camera = initialize_camera(
            config.CAMERA_INDEX, 
            config.CAMERA_WIDTH, 
            config.CAMERA_HEIGHT
        )
        detector = YOLOPersonDetector(config)
        
        cv2.namedWindow("Calibration Tool", cv2.WINDOW_NORMAL)
        
        print("\nCalibration started. Position yourself at different distances...\n")
        
        last_bbox_height = 0
        
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Failed to read frame")
                break
            
            # Detect person
            person_detected, bbox, distance_status, confidence = detector.detect_person(frame)
            
            # Draw detection
            if bbox:
                x1, y1, x2, y2 = bbox
                bbox_height = y2 - y1
                bbox_width = x2 - x1
                last_bbox_height = bbox_height
                
                # Color based on distance
                if distance_status == 'very_near':
                    color = (0, 255, 0)  # Green
                    label = "VERY CLOSE (≤0.6m)"
                    key_hint = "Press 'v' to save"
                elif distance_status == 'near':
                    color = (0, 255, 255)  # Yellow
                    label = "NEAR (~3m)"
                    key_hint = "Press 'n' to save"
                else:
                    color = (0, 165, 255)  # Orange
                    label = "FAR (>5m)"
                    key_hint = "Press 'f' to save"
                
                # Draw bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw info panel with dark background
                panel_h = 350
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (600, panel_h), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                # Info text
                info_y = 40
                line_spacing = 45
                
                cv2.putText(frame, f"Status: {label}", (20, info_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                cv2.putText(frame, f"Bbox Height: {bbox_height}px", (20, info_y + line_spacing), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                
                cv2.putText(frame, f"Bbox Width: {bbox_width}px", (20, info_y + line_spacing*2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                
                cv2.putText(frame, f"Confidence: {confidence:.2f}", (20, info_y + line_spacing*3), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                
                # Key hint
                cv2.putText(frame, key_hint, (20, info_y + line_spacing*4), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                
                # Current thresholds
                thresh_y = info_y + line_spacing*5
                cv2.putText(frame, "Current Thresholds:", (20, thresh_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
                cv2.putText(frame, f"FAR: < {current_config['distance_far']}px", 
                           (30, thresh_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 1)
                cv2.putText(frame, f"NEAR: {current_config['distance_far']}-{current_config['distance_near']}px", 
                           (30, thresh_y + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                cv2.putText(frame, f"VERY_NEAR: > {current_config['distance_very_near']}px", 
                           (30, thresh_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            
            else:
                cv2.putText(frame, "NO PERSON DETECTED", (20, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                cv2.putText(frame, "Stand in front of camera", (20, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
            
            # Show measurements collected
            measurements_y = frame.shape[0] - 150
            cv2.putText(frame, "Measurements Collected:", (20, measurements_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, f"FAR: {len(measurements['far'])} samples", 
                       (30, measurements_y + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            cv2.putText(frame, f"NEAR: {len(measurements['near'])} samples", 
                       (30, measurements_y + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"VERY NEAR: {len(measurements['very_near'])} samples", 
                       (30, measurements_y + 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Instructions at bottom
            cv2.putText(frame, "Press 's' to SAVE config  |  Press 'q' to QUIT", 
                       (20, frame.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display
            cv2.imshow("Calibration Tool", frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\nExiting without saving...")
                break
            
            elif key == ord('f') and bbox:
                # Save as FAR
                measurements['far'].append(last_bbox_height)
                print(f"FAR measurement saved: {last_bbox_height}px "
                      f"(Total: {len(measurements['far'])})")
            
            elif key == ord('n') and bbox:
                # Save as NEAR
                measurements['near'].append(last_bbox_height)
                print(f"NEAR measurement saved: {last_bbox_height}px "
                      f"(Total: {len(measurements['near'])})")
            
            elif key == ord('v') and bbox:
                # Save as VERY NEAR
                measurements['very_near'].append(last_bbox_height)
                print(f"VERY NEAR measurement saved: {last_bbox_height}px "
                      f"(Total: {len(measurements['very_near'])})")
            
            elif key == ord('s'):
                # Save configuration
                if any(len(v) > 0 for v in measurements.values()):
                    print("\nSaving calibration to config/kiosk_config.json...")
                    new_config = save_calibration_config(measurements, current_config)
                    print("Configuration saved successfully!")
                    print(f"\nNew thresholds:")
                    print(f"   distance_far: {new_config['distance_far']}")
                    print(f"   distance_near: {new_config['distance_near']}")
                    print(f"   distance_very_near: {new_config['distance_very_near']}")
                    break
                else:
                    print("\nNo measurements collected! Take some measurements first.")
        
        # Cleanup
        camera.release()
        cv2.destroyAllWindows()
        
        # Show summary
        print("\n" + "="*70)
        print("                    CALIBRATION SUMMARY")
        print("="*70)
        
        if any(len(v) > 0 for v in measurements.values()):
            print("\nMeasurements collected:")
            
            for dist_type, values in measurements.items():
                if values:
                    avg = sum(values) / len(values)
                    min_val = min(values)
                    max_val = max(values)
                    print(f"\n  {dist_type.upper()}:")
                    print(f"    Samples: {len(values)}")
                    print(f"    Values: {values}")
                    print(f"    Average: {avg:.1f}px")
                    print(f"    Range: {min_val}-{max_val}px")
            
            print("\n" + "="*70)
            print("Calibration complete!")
            print(f"Config saved to: {CONFIG_PATH}")
            print("\nTIP: Run this calibration in your actual deployment environment")
            print("   for best results. Lighting and camera angle affect measurements.")
        
        else:
            print("\nNo measurements collected!")
            print("Run the tool again and use 'f', 'n', 'v' keys to save measurements.")
        
        print("\n" + "="*70)
        input("\nPress Enter to exit...")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()