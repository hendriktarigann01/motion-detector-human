"""
Camera Helper - Initialize and configure camera
"""

import cv2
import logging

logger = logging.getLogger(__name__)


def initialize_camera(camera_index=0, width=1280, height=720):
    """
    Initialize camera with specified settings
    
    Args:
        camera_index (int): Camera index (0 for default/laptop camera)
        width (int): Frame width
        height (int): Frame height
    
    Returns:
        cv2.VideoCapture: Initialized camera object
    
    Raises:
        RuntimeError: If camera cannot be initialized
    """
    try:
        logger.info(f"Attempting to initialize camera index {camera_index}")
        
        # Open camera
        camera = cv2.VideoCapture(camera_index)
        
        if not camera.isOpened():
            raise RuntimeError(f"Cannot open camera at index {camera_index}")
        
        # Set resolution
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Verify settings
        actual_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        logger.info(f"Camera initialized successfully")
        logger.info(f"Resolution: {int(actual_width)}x{int(actual_height)}")
        
        # Set buffer size (reduce latency)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        return camera
    
    except Exception as e:
        logger.error(f"Failed to initialize camera: {e}")
        raise RuntimeError(f"Camera initialization failed: {e}")


def test_camera(camera_index=0, duration=5):
    """
    Test camera by showing preview for specified duration
    
    Args:
        camera_index (int): Camera to test
        duration (int): Test duration in seconds
    """
    import time
    
    print(f"Testing camera {camera_index} for {duration} seconds...")
    print("Press 'q' to exit early")
    
    try:
        camera = initialize_camera(camera_index)
        start_time = time.time()
        
        while (time.time() - start_time) < duration:
            ret, frame = camera.read()
            
            if not ret:
                print("Failed to read frame")
                break
            
            # Add info text
            cv2.putText(frame, f"Camera {camera_index} Test", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to exit", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow("Camera Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.release()
        cv2.destroyAllWindows()
        print("Camera test completed successfully!")
        
    except Exception as e:
        print(f"Camera test failed: {e}")


if __name__ == "__main__":
    # Run camera test
    test_camera(camera_index=0, duration=10)