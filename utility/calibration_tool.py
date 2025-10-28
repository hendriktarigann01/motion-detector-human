"""
Distance Calibration Tool
Helps calibrate DISTANCE thresholds for your specific camera setup
"""

import cv2
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings as config
from models.yolo_detector import YOLOPersonDetector
from helpers.camera_helper import initialize_camera

print("="*60)
print("DISTANCE CALIBRATION TOOL")
print("="*60)
print()
print("This tool helps you calibrate distance thresholds.")
print()
print("Instructions:")
print("1. Stand at approximately 5 meters from camera")
print("2. Note the 'Bbox Height' value")
print("3. Stand at approximately 0.6 meters from camera")
print("4. Note the 'Bbox Height' value")
print("5. Update config/settings.py with these values")
print()
print("Controls:")
print("- Press 'q' to quit")
print("- Press 's' to save current bbox height")
print()
print("="*60)

# Storage for saved measurements
measurements = {
    'far': [],
    'near': [],
    'very_near': []
}

def main():
    try:
        # Initialize
        camera = initialize_camera(config.CAMERA_INDEX, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
        detector = YOLOPersonDetector(config)
        
        cv2.namedWindow("Calibration Tool", cv2.WINDOW_NORMAL)
        
        print("\nCalibration started. Position yourself at different distances...")
        
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
                
                # Color based on distance
                if distance_status == 'very_near':
                    color = (0, 255, 0)  # Green
                    label = "VERY CLOSE (≤0.6m)"
                elif distance_status == 'near':
                    color = (0, 255, 255)  # Yellow
                    label = "NEAR (<5m)"
                else:
                    color = (0, 165, 255)  # Orange
                    label = "FAR (>5m)"
                
                # Draw bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw info panel
                info_y = 50
                cv2.putText(frame, f"Status: {label}", (10, info_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                cv2.putText(frame, f"Bbox Height: {bbox_height}px", (10, info_y + 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"Bbox Width: {bbox_width}px", (10, info_y + 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, info_y + 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Draw instructions
                cv2.putText(frame, "Press 's' to save measurement", (10, frame.shape[0] - 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Show current thresholds
                thresh_y = info_y + 180
                cv2.putText(frame, "Current Thresholds:", (10, thresh_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
                cv2.putText(frame, f"FAR: < {config.DISTANCE_FAR}px", (10, thresh_y + 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 1)
                cv2.putText(frame, f"NEAR: > {config.DISTANCE_NEAR}px", (10, thresh_y + 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                cv2.putText(frame, f"VERY_NEAR: > {config.DISTANCE_VERY_NEAR}px", (10, thresh_y + 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            
            else:
                cv2.putText(frame, "NO PERSON DETECTED", (10, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Stand in front of camera", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display
            cv2.imshow("Calibration Tool", frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            
            elif key == ord('s') and bbox:
                # Save measurement
                print(f"\n📏 Measurement saved: {bbox_height}px ({distance_status})")
                measurements[distance_status].append(bbox_height)
                
                # Give feedback
                print(f"   Total measurements: FAR={len(measurements['far'])}, "
                      f"NEAR={len(measurements['near'])}, VERY_NEAR={len(measurements['very_near'])}")
        
        # Cleanup
        camera.release()
        cv2.destroyAllWindows()
        
        # Show summary
        print("\n" + "="*60)
        print("CALIBRATION SUMMARY")
        print("="*60)
        
        if any(len(v) > 0 for v in measurements.values()):
            print("\nMeasurements collected:")
            
            for dist_type, values in measurements.items():
                if values:
                    avg = sum(values) / len(values)
                    print(f"  {dist_type.upper()}: {values} → Average: {avg:.1f}px")
            
            print("\n📝 RECOMMENDED THRESHOLDS:")
            print("Update config/settings.py with these values:\n")
            
            # Calculate recommended thresholds
            if measurements['very_near']:
                very_near_min = min(measurements['very_near'])
                print(f"DISTANCE_VERY_NEAR = {int(very_near_min * 0.9)}  # ≤0.6m")
            
            if measurements['near']:
                near_min = min(measurements['near'])
                print(f"DISTANCE_NEAR = {int(near_min * 0.9)}  # <5m")
            
            if measurements['far']:
                far_max = max(measurements['far'])
                print(f"DISTANCE_FAR = {int(far_max * 1.1)}  # >5m")
            
            print("\n💡 TIP: Add 10-20% margin to avoid false transitions")
        
        else:
            print("\n⚠️  No measurements collected!")
            print("Run the tool again and press 's' to save measurements.")
        
        print("\n" + "="*60)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()