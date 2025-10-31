"""
C-Merch Kiosk - Main Application (OPTIMIZED)
FIXES:
- FPS boost: Skip YOLO in Stage 1 & 4, optimize video decoding
- Button always visible in Stage 3 (fixed z-index)
- Remove camera preview/border in production mode
- Cleaner code structure
"""

import cv2
import time
import logging
from datetime import datetime
import sys
from pathlib import Path
import numpy as np

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


class ClickableButton:
    """Interactive button (Stage 3 only)"""
    
    def __init__(self, x, y, width, height, text, config):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.text = text
        self.config = config
        self.is_hovered = False
        self.is_clicked = False
    
    def contains_point(self, px, py):
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def update_hover(self, mouse_x, mouse_y):
        self.is_hovered = self.contains_point(mouse_x, mouse_y)
    
    def click(self, mouse_x, mouse_y):
        if self.contains_point(mouse_x, mouse_y):
            self.is_clicked = True
            logger.info(f"Button '{self.text}' clicked!")
            return True
        return False
    
    def draw(self, frame):
        """Draw button with clear visibility"""
        color = self.config.BUTTON_HOVER_COLOR if self.is_hovered else self.config.BUTTON_COLOR
        
        # Filled rectangle
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     color, -1)
        
        # White border
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     (255, 255, 255), 3)
        
        # Centered text
        text_size = cv2.getTextSize(self.text, cv2.FONT_HERSHEY_SIMPLEX, 
                                   self.config.BUTTON_FONT_SCALE, 
                                   self.config.BUTTON_FONT_THICKNESS)[0]
        text_x = self.x + (self.width - text_size[0]) // 2
        text_y = self.y + (self.height + text_size[1]) // 2
        
        cv2.putText(frame, self.text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   self.config.BUTTON_FONT_SCALE,
                   self.config.BUTTON_TEXT_COLOR,
                   self.config.BUTTON_FONT_THICKNESS)
    
    def reset(self):
        self.is_clicked = False
        self.is_hovered = False


class TransitionManager:
    """Fade transitions between states"""
    
    def __init__(self, config):
        self.config = config
        self.is_transitioning = False
        self.transition_start = None
        self.fade_duration = config.FADE_DURATION
    
    def start_transition(self, from_state, to_state):
        self.is_transitioning = True
        self.transition_start = time.time()
        if config.DEVELOPMENT_MODE:
            logger.info(f"Transition: {from_state.value} → {to_state.value}")
    
    def get_fade_alpha(self):
        """Returns (alpha, is_complete)"""
        if not self.is_transitioning:
            return 0.0, True
        
        elapsed = time.time() - self.transition_start
        progress = elapsed / self.fade_duration
        
        if progress >= 1.0:
            self.is_transitioning = False
            return 0.0, True
        
        # Fade out then fade in
        alpha = progress * 2 if progress < 0.5 else (1.0 - progress) * 2
        return alpha, False
    
    def apply_fade(self, frame):
        if not self.is_transitioning:
            return frame
        
        alpha, _ = self.get_fade_alpha()
        overlay = np.zeros_like(frame)
        return cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
    
    def is_mid_transition(self):
        if not self.is_transitioning:
            return False
        elapsed = time.time() - self.transition_start
        progress = elapsed / self.fade_duration
        return 0.4 < progress < 0.6


class KioskApplication:
    """Main Kiosk Application"""
    
    def __init__(self):
        logger.info("="*60)
        logger.info("C-Merch Kiosk - OPTIMIZED VERSION")
        logger.info(f"Resolution: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
        logger.info(f"Mode: {'DEVELOPMENT' if config.DEVELOPMENT_MODE else 'PRODUCTION'}")
        logger.info("="*60)
        
        # Core components
        self.camera = None
        self.yolo_detector = YOLOPersonDetector(config)
        self.state_machine = StateMachine(config)
        self.media_player = MediaPlayer(config)
        self.web_handler = WebInterfaceHandler(config)
        self.fps_counter = FPSCounter(smoothing_interval=config.FPS_SMOOTHING_INTERVAL)
        self.transition_manager = TransitionManager(config)
        
        self.running = False
        self.pending_state_change = None
        self.mouse_x, self.mouse_y = 0, 0
        self.more_info_button = None
        
        # Start welcome animation immediately
        self.media_player.play_welcome_animation()
        
        # Setup window
        self.window_name = config.WINDOW_NAME
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        if config.FULLSCREEN_MODE:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.resizeWindow(self.window_name, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
        
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        # Create button (bottom-right)
        self._create_button()
    
    def _create_button(self):
        # TEMP: Move button to center of screen for testing visibility
        btn_x = (config.CAMERA_WIDTH - config.BUTTON_WIDTH) // 3
        btn_y = (config.CAMERA_HEIGHT - config.BUTTON_HEIGHT) // 3

        self.more_info_button = ClickableButton(
            btn_x, btn_y, config.BUTTON_WIDTH, config.BUTTON_HEIGHT,
            "More Information", config
        )
    
    def _mouse_callback(self, event, x, y, flags, param):
        self.mouse_x, self.mouse_y = x, y
        
        # Update hover in Stage 3
        if self.state_machine.current_state == KioskState.STAGE_3_AUDIO:
            if self.more_info_button:
                self.more_info_button.update_hover(x, y)
        
        # Handle click
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.state_machine.current_state == KioskState.STAGE_3_AUDIO:
                if self.more_info_button and self.more_info_button.click(x, y):
                    self.state_machine.signal_button_click()
    
    def initialize(self):
        try:
            self.camera = initialize_camera(
                config.CAMERA_INDEX, 
                config.CAMERA_WIDTH, 
                config.CAMERA_HEIGHT
            )
            logger.info("Camera initialized")
            self.running = True
            return True
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def run(self):
        if not self.initialize():
            return

        logger.info("Starting main loop...")
        
        try:
            while self.running:
                self._process_frame()
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q'):
                    break
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def _process_frame(self):
        """OPTIMIZED: Skip YOLO when not needed"""
        ret, frame = self.camera.read()
        if not ret:
            return
        
        self.fps_counter.update_frame_rate()
        current_state = self.state_machine.current_state
        
        # OPTIMIZATION: Only skip YOLO in Stage 4 (web active)
        if current_state == KioskState.STAGE_4_WEB:
            # Skip YOLO in Stage 4 for FPS boost
            person_detected, bbox, distance_status, confidence = False, None, None, 0.0
        else:
            # Run YOLO in Stage 1, 2, 3 (need person detection)
            person_detected, bbox, distance_status, confidence = self.yolo_detector.detect_person(frame)
            
        # Check web interaction
        interaction_detected = False
        web_completed = False
        if current_state == KioskState.STAGE_4_WEB:
            interaction_detected = self.web_handler.check_interaction()
            web_completed = self.web_handler.check_completion()
        
        # Update state machine
        button_clicked = self.state_machine.button_clicked
        state_changed, current_state = self.state_machine.update(
            person_detected, distance_status, 
            interaction_detected, web_completed, button_clicked
        )
        
        # Handle state changes
        if state_changed:
            self._queue_state_change(current_state)
            if self.more_info_button:
                self.more_info_button.reset()
        
        # Render display
        display_frame = self._render_display(frame, current_state, bbox, distance_status, confidence)
        cv2.imshow(self.window_name, display_frame)
    
    def _queue_state_change(self, new_state):
        if not self.transition_manager.is_transitioning:
            old_state = self.state_machine.previous_state
            self.transition_manager.start_transition(old_state, new_state)
            self.pending_state_change = new_state
    
    def _execute_state_change(self, new_state):
        """Execute state change at mid-transition"""
        if new_state == KioskState.STAGE_1_IDLE:
            self.media_player.play_welcome_animation()
            self.web_handler.close_browser()
        
        elif new_state == KioskState.STAGE_2_DETECTED:
            logger.info("DEBUG: Executing Stage 2 - playing handwaving video and audio")
            self.media_player.play_handwaving_video_and_audio()
        
        elif new_state == KioskState.STAGE_3_AUDIO:
            pass  # Audio continues from Stage 2
        
        elif new_state == KioskState.STAGE_4_WEB:
            self.media_player.stop_all()
            self.web_handler.open_browser()
    
    def _render_display(self, camera_frame, current_state, bbox, distance_status, confidence):
        """OPTIMIZED rendering"""
        h, w = camera_frame.shape[:2]

        # Stage 1, 2, 3: Video display
        if current_state in [KioskState.STAGE_1_IDLE,
                            KioskState.STAGE_2_DETECTED,
                            KioskState.STAGE_3_AUDIO]:

            video_frame = self.media_player.get_video_frame((w, h), loop=True)
            display = video_frame if video_frame is not None else camera_frame.copy()

            # STAGE 3: Draw button (ONLY WHEN VERY NEAR)
            if current_state == KioskState.STAGE_3_AUDIO and self.more_info_button and distance_status == "VERY_NEAR":
                self.more_info_button.draw(display)
                # DEBUG: Add button status overlay
                if config.DEVELOPMENT_MODE:
                    cv2.putText(display, "BUTTON DRAWN: YES (VERY NEAR)", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Debug info (DEVELOPMENT_MODE only)
            if config.DEVELOPMENT_MODE:
                # Small camera preview (top-left)
                small = cv2.resize(camera_frame, (w//4, h//4))
                display[10:10+h//4, 10:10+w//4] = small

                # Stage indicator
                if current_state == KioskState.STAGE_3_AUDIO:
                    cv2.putText(display, "STAGE 3: BUTTON VISIBLE",
                               (10, h - 30), cv2.FONT_HERSHEY_SIMPLEX,
                               0.8, (0, 255, 0), 2)

                # YOLO detection
                if bbox is not None:
                    display = self.yolo_detector.draw_detection(
                        display, bbox, distance_status, confidence
                    )

        # Stage 4: Web interface
        elif current_state == KioskState.STAGE_4_WEB:
            display = np.zeros((h, w, 3), dtype=np.uint8)

            # Small camera (bottom-right, DEVELOPMENT_MODE only)
            if config.DEVELOPMENT_MODE:
                small_h, small_w = h//4, w//4
                small = cv2.resize(camera_frame, (small_w, small_h))
                display[h-small_h-10:h-10, w-small_w-10:w-10] = small

            # Text
            text = "Web Interface Active"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            cv2.putText(display, text,
                       ((w - text_size[0])//2, h//2),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        else:
            display = camera_frame.copy()

        # DEBUG: Force button visibility in Stage 3 for testing
        if current_state == KioskState.STAGE_3_AUDIO and self.more_info_button and config.DEVELOPMENT_MODE:
            # Draw button directly on display regardless of z-index issues
            self.more_info_button.draw(display)
            # Add extra debug info
            cv2.putText(display, "BUTTON FORCED DRAW", (10, 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

        # Overlay (state info, FPS, etc.)
        display = self._draw_overlay(display, current_state, distance_status)

        # Apply fade transition
        if self.transition_manager.is_transitioning:
            if self.transition_manager.is_mid_transition() and self.pending_state_change:
                self._execute_state_change(self.pending_state_change)
                self.pending_state_change = None
            display = self.transition_manager.apply_fade(display)

        return display
    
    def _draw_overlay(self, frame, current_state, distance_status):
        """Draw info overlay"""
        h, w = frame.shape[:2]
        
        # State text (top-left)
        cv2.putText(frame, f"State: {current_state.value}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # FPS (top-right)
        if config.SHOW_FPS:
            fps_text = f"FPS: {self.fps_counter.get_fps():.1f}"
            text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(frame, fps_text, (w - text_size[0] - 10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # DEVELOPMENT_MODE: Extra debug info
        if config.DEVELOPMENT_MODE:
            # Distance status
            if distance_status:
                cv2.putText(frame, f"Distance: {distance_status}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Stage 2: FAR timer
            if current_state == KioskState.STAGE_2_DETECTED:
                far_time = self.state_machine.get_far_duration()
                if far_time > 0:
                    cv2.putText(frame, f"FAR: {far_time:.1f}s / {config.STAGE2_FAR_TIMEOUT}s", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
            
            # Stage 3: Very near timer
            if current_state == KioskState.STAGE_3_AUDIO:
                vn_time = self.state_machine.get_very_near_duration()
                cv2.putText(frame, f"Very Near: {vn_time:.1f}s (Click Required)", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Countdown
            countdown = self.state_machine.get_countdown_remaining()
            if countdown and countdown > 0:
                countdown_text = f"Countdown: {int(countdown)}s"
                text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
                x, y = (w - text_size[0])//2, (h + text_size[1])//2
                cv2.rectangle(frame, (x-10, y-text_size[1]-10), 
                            (x+text_size[0]+10, y+10), (0, 0, 0), -1)
                cv2.putText(frame, countdown_text, (x, y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        
        return frame
    
    def cleanup(self):
        logger.info("Cleaning up...")
        self.running = False
        
        if self.camera:
            self.camera.release()
        
        self.media_player.cleanup()
        self.web_handler.cleanup()
        cv2.destroyAllWindows()
        
        logger.info("Cleanup complete")


def main():
    app = KioskApplication()
    app.run()


if __name__ == "__main__":
    main()