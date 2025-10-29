"""
MJ Solution Kiosk - Main Application
UPDATED: 
- Welcome animation (Stage 1)
- Hand-waving video+audio (Stage 2 & 3)
- "More Information" button (Stage 3 only)
- Portrait window size with proper scaling
- Smooth fade transitions (1 sec black)
- NO AUTO-DIRECT: Must click button to go to web
- Auto fullscreen (F11) when web opens
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
    """Interactive button for UI"""
    
    def __init__(self, x, y, width, height, text, config):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.config = config
        self.is_hovered = False
        self.is_clicked = False
    
    def contains_point(self, px, py):
        """Check if point (px, py) is inside button"""
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)
    
    def update_hover(self, mouse_x, mouse_y):
        """Update hover state"""
        self.is_hovered = self.contains_point(mouse_x, mouse_y)
    
    def click(self, mouse_x, mouse_y):
        """Check if button was clicked"""
        if self.contains_point(mouse_x, mouse_y):
            self.is_clicked = True
            if config.DEVELOPMENT_MODE:
                logger.info(f"Button '{self.text}' clicked!")
            return True
        return False
    
    def draw(self, frame):
        """Draw button on frame"""
        # Choose color based on hover state
        color = self.config.BUTTON_HOVER_COLOR if self.is_hovered else self.config.BUTTON_COLOR
        
        # Draw button rectangle
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     color, -1)
        
        # Draw border
        cv2.rectangle(frame, (self.x, self.y), 
                     (self.x + self.width, self.y + self.height), 
                     (255, 255, 255), 2)
        
        # Draw text (centered)
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
        """Reset button state"""
        self.is_clicked = False
        self.is_hovered = False


class TransitionManager:
    """Manages smooth fade transitions between states"""
    
    def __init__(self, config):
        self.config = config
        self.is_transitioning = False
        self.transition_start_time = None
        self.transition_from_state = None
        self.transition_to_state = None
        self.fade_duration = config.FADE_DURATION
        self.fade_color = config.FADE_COLOR
    
    def start_transition(self, from_state, to_state):
        """Start a fade transition"""
        self.is_transitioning = True
        self.transition_start_time = time.time()
        self.transition_from_state = from_state
        self.transition_to_state = to_state
        if config.DEVELOPMENT_MODE:
            logger.info(f"Starting fade transition: {from_state.value} -> {to_state.value}")
    
    def get_fade_alpha(self):
        """
        Get current fade alpha value (0.0 to 1.0)
        Returns: (fade_out_alpha, is_complete)
        - First half: fade to black (0 -> 1)
        - Second half: fade from black (1 -> 0)
        """
        if not self.is_transitioning:
            return 0.0, True
        
        elapsed = time.time() - self.transition_start_time
        progress = elapsed / self.fade_duration
        
        if progress >= 1.0:
            # Transition complete
            self.is_transitioning = False
            return 0.0, True
        
        # First half: fade out (0 -> 1)
        # Second half: fade in (1 -> 0)
        if progress < 0.5:
            alpha = progress * 2  # 0 -> 1
        else:
            alpha = (1.0 - progress) * 2  # 1 -> 0
        
        return alpha, False
    
    def apply_fade(self, frame):
        """Apply fade effect to frame"""
        if not self.is_transitioning:
            return frame
        
        alpha, _ = self.get_fade_alpha()
        
        # Create black overlay
        overlay = np.full_like(frame, self.fade_color, dtype=np.uint8)
        
        # Blend frame with overlay
        faded_frame = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
        
        return faded_frame
    
    def is_mid_transition(self):
        """Check if we're at the midpoint of transition (fully black)"""
        if not self.is_transitioning:
            return False
        
        elapsed = time.time() - self.transition_start_time
        progress = elapsed / self.fade_duration
        
        # Midpoint is at 0.5 (fully black)
        return 0.4 < progress < 0.6


class KioskApplication:
    """Main Kiosk Application"""
    
    def __init__(self):
        logger.info("="*60)
        logger.info("MJ Solution Kiosk Application Starting...")
        logger.info(f"Resolution: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} (Portrait 9:16)")
        if config.DEVELOPMENT_MODE:
            logger.info("DEVELOPMENT MODE: ON")
        logger.info("="*60)
        
        self.camera = None
        self.yolo_detector = YOLOPersonDetector(config)
        self.state_machine = StateMachine(config)
        self.media_player = MediaPlayer(config)
        self.web_handler = WebInterfaceHandler(config)
        self.fps_counter = FPSCounter(smoothing_interval=config.FPS_SMOOTHING_INTERVAL)
        self.transition_manager = TransitionManager(config)
        
        self.last_time = time.time()
        self.running = False
        
        # State change handling
        self.pending_state_change = None
        
        # Mouse tracking
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Button (created after window is ready)
        self.more_info_button = None
        
        # Start welcome animation IMMEDIATELY (before camera)
        if config.DEVELOPMENT_MODE:
            logger.info("Starting welcome animation...")
        self.media_player.play_welcome_animation()
        
        # Create window with PORTRAIT aspect ratio
        self.window_name = config.WINDOW_NAME
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        # Set window size to match portrait resolution (don't use fullscreen for development)
        if not config.FULLSCREEN_MODE:
            cv2.resizeWindow(self.window_name, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
        else:
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Set mouse callback
        cv2.setMouseCallback(self.window_name, self._mouse_callback)
        
        # Create button (bottom right corner)
        self._create_button()
    
    def _create_button(self):
        """Create 'More Information' button"""
        btn_x = config.CAMERA_WIDTH - config.BUTTON_WIDTH - config.BUTTON_PADDING
        btn_y = config.CAMERA_HEIGHT - config.BUTTON_HEIGHT - config.BUTTON_PADDING
        
        self.more_info_button = ClickableButton(
            x=btn_x,
            y=btn_y,
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            text="More Information",
            config=config
        )
        if config.DEVELOPMENT_MODE:
            logger.info(f"Button created at ({btn_x}, {btn_y})")
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events"""
        # Update mouse position
        self.mouse_x = x
        self.mouse_y = y
        
        # Update button hover state (only in Stage 3)
        if self.state_machine.current_state == KioskState.STAGE_3_AUDIO:
            if self.more_info_button:
                self.more_info_button.update_hover(x, y)
        
        # Handle click
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.state_machine.current_state == KioskState.STAGE_3_AUDIO:
                if self.more_info_button and self.more_info_button.click(x, y):
                    # Button was clicked, signal state machine
                    self.state_machine.signal_button_click()
    
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

                # Non-blocking key check
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
        button_clicked = self.state_machine.button_clicked  # Check if button was clicked
        
        if self.state_machine.current_state == KioskState.STAGE_4_WEB:
            interaction_detected = self.web_handler.check_interaction()
            web_completed = self.web_handler.check_completion()
        
        # Update state machine (NO AUTO-TRIGGER, only button click)
        state_changed, current_state = self.state_machine.update(
            person_detected, distance_status, interaction_detected, web_completed, button_clicked
        )
        
        # Handle state changes with smooth transitions
        if state_changed:
            self._queue_state_change(current_state)
            # Reset button when leaving Stage 3
            if self.more_info_button:
                self.more_info_button.reset()
        
        # Render display
        display_frame = self._render_display(frame, current_state, bbox, distance_status, confidence)
        
        cv2.imshow(self.window_name, display_frame)
    
    def _queue_state_change(self, new_state):
        """Queue a state change with fade transition"""
        if not self.transition_manager.is_transitioning:
            old_state = self.state_machine.previous_state
            self.transition_manager.start_transition(old_state, new_state)
            self.pending_state_change = new_state
    
    def _execute_state_change(self, new_state):
        """Execute the actual state change (called at mid-transition)"""
        if config.DEVELOPMENT_MODE:
            logger.info(f"Executing state change: {new_state.value}")
        
        if new_state == KioskState.STAGE_1_IDLE:
            # Stage 1: Play welcome animation
            self.media_player.play_welcome_animation()
            self.web_handler.close_browser()
        
        elif new_state == KioskState.STAGE_2_DETECTED:
            # Stage 2: Play hand-waving video + audio
            self.media_player.play_handwaving_video_and_audio()
        
        elif new_state == KioskState.STAGE_3_AUDIO:
            # Stage 3: Continue hand-waving video + audio (already playing from Stage 2)
            # Button will appear in render
            pass
        
        elif new_state == KioskState.STAGE_4_WEB:
            # Stage 4: Open web interface with auto fullscreen (F11)
            self.media_player.stop_all()  
            self.web_handler.open_browser()
    
    def _render_display(self, camera_frame, current_state, bbox, distance_status, confidence):
        """Render display based on current state"""
        h, w = camera_frame.shape[:2]
        
        # Stage 1: Welcome animation
        # Stage 2 & 3: Hand-waving video + audio
        if current_state in [KioskState.STAGE_1_IDLE, KioskState.STAGE_2_DETECTED, 
                            KioskState.STAGE_3_AUDIO]:
            
            video_frame = self.media_player.get_video_frame(target_size=(w, h), loop=True)
            
            if video_frame is not None:
                display = video_frame.copy()
                
                # Debug: Show small camera feed
                if config.DEBUG_MODE:
                    small_camera = cv2.resize(camera_frame, (w//4, h//4))
                    display[10:10+h//4, 10:10+w//4] = small_camera
            else:
                display = camera_frame.copy()
            
            # Draw "More Information" button ONLY in Stage 3
            if current_state == KioskState.STAGE_3_AUDIO and self.more_info_button:
                self.more_info_button.draw(display)
        
        elif current_state == KioskState.STAGE_4_WEB:
            display = self._render_stage4_display(camera_frame)
        
        else:
            display = camera_frame.copy()
        
        # Draw YOLO detection (debug mode)
        if config.DEBUG_MODE and bbox is not None:
            display = self.yolo_detector.draw_detection(display, bbox, distance_status, confidence)
        
        # Draw overlay (state info, FPS, countdown)
        display = self._draw_overlay(display, current_state, distance_status)
        
        # Apply fade transition
        if self.transition_manager.is_transitioning:
            # Check if we're at mid-transition (fully black)
            if self.transition_manager.is_mid_transition() and self.pending_state_change:
                self._execute_state_change(self.pending_state_change)
                self.pending_state_change = None
            
            display = self.transition_manager.apply_fade(display)
        
        return display
    
    def _render_stage4_display(self, camera_frame):
        """Render display for Stage 4 (web interface active)"""
        h, w = camera_frame.shape[:2]
        
        # Black background
        display = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Small camera preview (bottom right)
        small_h, small_w = h//4, w//4
        small_camera = cv2.resize(camera_frame, (small_w, small_h))
        display[h-small_h-10:h-10, w-small_w-10:w-10] = small_camera
        
        # Text
        text = "Web Interface Active"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        text_x = (w - text_size[0]) // 2
        text_y = h // 2
        cv2.putText(display, text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        return display
    
    def _draw_overlay(self, frame, current_state, distance_status):
        """Draw state info and countdown overlay"""
        h, w = frame.shape[:2]
        
        # State text
        state_text = f"State: {current_state.value}"
        cv2.putText(frame, state_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # FPS
        if config.SHOW_FPS:
            fps_text = f"FPS: {self.fps_counter.get_fps():.1f}"
            text_size = cv2.getTextSize(fps_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.putText(frame, fps_text, (w - text_size[0] - 10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Distance status
        if distance_status and config.DEVELOPMENT_MODE:
            dist_text = f"Distance: {distance_status}"
            cv2.putText(frame, dist_text, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Very near progress (Stage 3) - only in development mode
        if current_state == KioskState.STAGE_3_AUDIO and config.DEVELOPMENT_MODE:
            very_near_time = self.state_machine.get_very_near_duration()
            progress_text = f"Very Near: {very_near_time:.1f}s / 3.0s"
            cv2.putText(frame, progress_text, (10, 110), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Countdown - only show in development mode
        countdown = self.state_machine.get_countdown_remaining()
        if countdown is not None and countdown > 0 and config.DEVELOPMENT_MODE:
            countdown_text = f"Countdown: {int(countdown)}s"
            text_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
            
            x = (w - text_size[0]) // 2
            y = (h + text_size[1]) // 2
            
            # Black background
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