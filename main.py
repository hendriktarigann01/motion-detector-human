"""
MJ Solution Kiosk - Main Application
MINIMAL FIXES: Only 3 changes marked with # FIXED
"""

import cv2
import time
import logging
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from config import settings as config
from models.yolo_detector import YOLOPersonDetector
from models.state_machine import StateMachine, KioskState
from models.fps_calculator import FPSCounter
from helpers.media_player import MediaPlayer
from helpers.web_interface import WebInterfaceHandler
from helpers.camera_helper import initialize_camera

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE) if config.SAVE_LOGS else logging.NullHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KioskApplication:
    """Main Kiosk Application"""
    
    def __init__(self):
        logger.info("="*60)
        logger.info("MJ Solution Kiosk Application Starting...")
        logger.info("="*60)
        
        self.camera = None
        self.yolo_detector = YOLOPersonDetector(config)
        self.state_machine = StateMachine(config)
        self.media_player = MediaPlayer(config)
        self.web_handler = WebInterfaceHandler(config)
        self.fps_counter = FPSCounter(smoothing_interval=config.FPS_SMOOTHING_INTERVAL)
        
        self.last_time = time.time()
        self.running = False
        
        # FIXED 1/3: Start idle video IMMEDIATELY (before camera)
        logger.info("▶️ Starting idle video...")
        self.media_player.play_idle_video()
        
        self.window_name = config.WINDOW_NAME
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        if config.FULLSCREEN_MODE:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    def initialize(self):
        """Initialize camera and other resources"""
        try:
            logger.info("Initializing camera...")
            self.camera = initialize_camera(
                camera_index=config.CAMERA_INDEX,
                width=config.CAMERA_WIDTH,
                height=config.CAMERA_HEIGHT
            )
            logger.info("Camera initialized successfully")
            self.running = True
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            logger.error("Initialization failed, exiting")
            return

        logger.info("Starting main loop...")

        try:
            while self.running:
                current_time = time.time()
                delta_time = current_time - self.last_time
                self.last_time = current_time

                self._process_frame(delta_time)

                # langsung tunggu input tanpa delay (non-blocking)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q'):
                    logger.info("Exit key pressed")
                    break

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)

        finally:
            self.cleanup()
    
    def _process_frame(self, delta_time):
        """Process single frame"""
        ret, frame = self.camera.read()
        if not ret:
            logger.warning("Failed to read camera frame")
            return
        
        self.fps_counter.update_frame_rate()
        
        # Detect person with YOLO
        person_detected, bbox, distance_status, confidence = self.yolo_detector.detect_person(frame)
        
        # Check interaction and completion signal
        interaction_detected = False
        web_completed = False
        if self.state_machine.current_state == KioskState.STAGE_4_WEB:
            interaction_detected = self.web_handler.check_interaction()
            web_completed = self.web_handler.check_completion()
        
        # Update state machine
        state_changed, current_state = self.state_machine.update(
            person_detected, distance_status, interaction_detected, web_completed
        )
        
        # Handle state changes
        if state_changed:
            self._on_state_changed(current_state)
        
        # Render display
        display_frame = self._render_display(frame, current_state, bbox, distance_status, confidence)
        
        cv2.imshow(self.window_name, display_frame)
    
    def _on_state_changed(self, new_state):
        """Handle state change events"""
        logger.info(f"State changed to: {new_state.value}")
        
        if new_state == KioskState.STAGE_1_IDLE:
            # Stage 1: Play idle video
            self.media_player.play_idle_video()
            self.web_handler.close_browser()
        
        elif new_state == KioskState.STAGE_2_DETECTED:
            # Stage 2: Play hand waving video (loops)
            self.media_player.play_waving_video()
        
        elif new_state == KioskState.STAGE_3_AUDIO:
            # Stage 3: Play audio (loops) + show hand waving video
            self.media_player.play_audio()
            # Keep showing waving video during audio stage
        
        elif new_state == KioskState.STAGE_4_WEB:
            # Stage 4: Open web interface
            self.media_player.stop_all()  
            self.web_handler.open_browser()
        
        elif new_state == KioskState.STAGE_5_THANKYOU:
            # Stage 5: Play thank you video (once, no loop)
            self.web_handler.close_browser()
            self.media_player.play_thankyou_video()
    
    def _render_display(self, camera_frame, current_state, bbox, distance_status, confidence):
        """Render display based on current state"""
        h, w = camera_frame.shape[:2]
        
        # Stage 2 and 3 both show waving video (Stage 3 plays audio on top)
        if current_state in [KioskState.STAGE_1_IDLE, KioskState.STAGE_2_DETECTED, 
                            KioskState.STAGE_3_AUDIO, KioskState.STAGE_5_THANKYOU]:
            
            # Only Stage 5 doesn't loop
            loop_video = (current_state != KioskState.STAGE_5_THANKYOU)
            
            video_frame = self.media_player.get_video_frame(target_size=(w, h), loop=loop_video)
            
            # Check if thank you video finished
            if current_state == KioskState.STAGE_5_THANKYOU and self.media_player.is_video_finished():
                logger.info("Thank you video finished, resetting to Stage 1")
                self.state_machine._transition_to(KioskState.STAGE_1_IDLE)
                self._on_state_changed(KioskState.STAGE_1_IDLE)
            
            if video_frame is not None:
                display = video_frame.copy()
                
                if config.DEBUG_MODE:
                    small_camera = cv2.resize(camera_frame, (w//4, h//4))
                    display[10:10+h//4, 10:10+w//4] = small_camera
            else:
                display = camera_frame.copy()
        
        elif current_state == KioskState.STAGE_4_WEB:
            display = self._render_stage4_display(camera_frame)
        
        else:
            display = camera_frame.copy()
        
        if config.DEBUG_MODE and bbox is not None:
            display = self.yolo_detector.draw_detection(display, bbox, distance_status, confidence)
        
        display = self._draw_overlay(display, current_state, distance_status)
        
        return display
    
    def _render_stage4_display(self, camera_frame):
        """Render display for Stage 4 (web interface active)"""
        import numpy as np
        h, w = camera_frame.shape[:2]
        
        display = np.zeros((h, w, 3), dtype=np.uint8)
        
        small_h, small_w = h//4, w//4
        small_camera = cv2.resize(camera_frame, (small_w, small_h))
        display[h-small_h-10:h-10, w-small_w-10:w-10] = small_camera
        
        text = "Web Interface Active"
        cv2.putText(display, text, (w//2 - 200, h//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        return display
    
    def _draw_overlay(self, frame, current_state, distance_status):
        """Draw state info and countdown overlay"""
        h, w = frame.shape[:2]
        
        state_text = f"State: {current_state.value}"
        cv2.putText(frame, state_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if config.SHOW_FPS:
            fps_text = f"FPS: {self.fps_counter.get_fps():.1f}"
            text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(frame, fps_text, (w - text_size[0] - 10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if distance_status:
            dist_text = f"Distance: {distance_status}"
            cv2.putText(frame, dist_text, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # FIXED 3/3: Show very_near progress in Stage 3
        if current_state == KioskState.STAGE_3_AUDIO:
            very_near_time = self.state_machine.get_very_near_duration()
            progress_text = f"Very Near: {very_near_time:.1f}s / 3.0s"
            cv2.putText(frame, progress_text, (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        countdown = self.state_machine.get_countdown_remaining()
        if countdown is not None and countdown > 0:
            countdown_text = f"Countdown: {int(countdown)}s"
            text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
            
            x = (w - text_size[0]) // 2
            y = (h + text_size[1]) // 2
            
            cv2.rectangle(frame, (x-10, y-text_size[1]-10), (x+text_size[0]+10, y+10), (0, 0, 0), -1)
            cv2.putText(frame, countdown_text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        
        return frame
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up...")
        
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        self.media_player.cleanup()
        self.web_handler.cleanup()
        
        cv2.destroyAllWindows()
        
        logger.info("Cleanup complete")
        logger.info("="*60)


def main():
    """Entry point"""
    import numpy as np
    globals()['np'] = np
    
    app = KioskApplication()
    app.run()


if __name__ == "__main__":
    main()