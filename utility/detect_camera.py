"""
Camera Detection Tool
Detects all available cameras and shows preview
"""

import cv2
import sys

print("="*60)
print("CAMERA DETECTION TOOL")
print("="*60)
print()
print("Scanning for available cameras...")
print("Press 'q' to close preview and try next camera")
print("Press ESC to exit completely")
print()

available_cameras = []

# Scan cameras 0-10
for i in range(10):
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        # Try to read a frame
        ret, frame = cap.read()
        
        if ret and frame is not None:
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            camera_info = {
                'index': i,
                'width': width,
                'height': height,
                'fps': fps
            }
            
            available_cameras.append(camera_info)
            
            print(f"   Camera {i} found:")
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {fps:.1f}")
            print()
        
        cap.release()

if not available_cameras:
    print(" No cameras found!")
    print()
    print("Troubleshooting:")
    print("1. Check if webcam is plugged in")
    print("2. Check if webcam is being used by another app")
    print("3. Try unplugging and plugging back in")
    print("4. Restart your computer")
    sys.exit(1)

print("="*60)
print(f"Found {len(available_cameras)} camera(s)")
print("="*60)
print()

# Show preview for each camera
for camera_info in available_cameras:
    idx = camera_info['index']
    
    print(f"📹 Showing preview for Camera {idx}")
    print(f"   Resolution: {camera_info['width']}x{camera_info['height']}")
    print(f"   Press 'q' to try next camera")
    print(f"   Press ESC to exit")
    print()
    
    cap = cv2.VideoCapture(idx)
    window_name = f"Camera {idx} Preview"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print(f"   ⚠️  Failed to read frame from Camera {idx}")
            break
        
        # Add info overlay
        info_text = [
            f"Camera Index: {idx}",
            f"Resolution: {camera_info['width']}x{camera_info['height']}",
            f"FPS: {camera_info['fps']:.1f}",
            f"Frame: {frame_count}",
            "",
            "Press 'q' for next camera",
            "Press ESC to exit"
        ]
        
        y_offset = 30
        for line in info_text:
            cv2.putText(frame, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            y_offset += 30
        
        cv2.imshow(window_name, frame)
        frame_count += 1
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print(f"   Moving to next camera...")
            print()
            break
        elif key == 27:  # ESC
            print(f"   Exiting...")
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
    
    cap.release()
    cv2.destroyWindow(window_name)

cv2.destroyAllWindows()

# Summary
print("="*60)
print("SUMMARY")
print("="*60)
print()
print("Available cameras:")
for camera_info in available_cameras:
    idx = camera_info['index']
    width = camera_info['width']
    height = camera_info['height']
    fps = camera_info['fps']
    
    print(f"📹 Camera {idx}: {width}x{height} @ {fps:.1f}fps")

print()
print("="*60)
print("NEXT STEPS")
print("="*60)
print()
print("1. Identify which camera you want to use:")
print("   - Camera 0 is usually built-in/internal")
print("   - Camera 1+ are usually external webcams")
print()
print("2. Update config/settings.py:")
print(f"   CAMERA_INDEX = X  # Replace X with your camera index")
print()
print("Examples:")
for camera_info in available_cameras:
    idx = camera_info['index']
    camera_type = "Built-in (laptop)" if idx == 0 else "External webcam"
    print(f"   CAMERA_INDEX = {idx}  # {camera_type}")
print()
print("3. Run the application:")
print("   python main.py")
print()
print("="*60)