

from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KioskState(Enum):
    """Enum for kiosk stages"""
    STAGE_1_IDLE = "idle_monitoring"
    STAGE_2_DETECTED = "person_detected"
    STAGE_3_AUDIO = "audio_prompt"
    STAGE_4_WEB = "web_interface"


class StateMachine:
    """Manages kiosk state transitions and timers"""
    
    def __init__(self, config):
        self.config = config
        self.current_state = KioskState.STAGE_1_IDLE
        self.previous_state = None
        
        # Timers
        self.state_entry_time = datetime.now()
        self.last_interaction_time = datetime.now()
        self.countdown_start_time = None
        
        # NEW: Track when person is FAR in Stage 2
        self.far_start_time = None
        self.was_far = False
        
        # Separate timer for very_near stability check (NOT USED for auto-trigger anymore)
        self.very_near_start_time = None
        self.was_very_near = False
        
        # Flags
        self.is_counting_down = False
        self.person_detected = False
        self.web_completion_requested = False
        self.button_clicked = False
        
        logger.info("State Machine initialized at STAGE_1_IDLE")
    
    def update(self, person_detected, distance_status, interaction_detected=False, web_completed=False, button_clicked=False):
        """
        Update state machine based on inputs
        
        Args:
            person_detected (bool): Is person detected by YOLO
            distance_status (str): 'far', 'near', 'very_near'
            interaction_detected (bool): User interaction in Stage 4
            web_completed (bool): Web signals button "Selesai 5" clicked
            button_clicked (bool): "More Information" button clicked in Stage 3
        
        Returns:
            tuple: (state_changed, new_state)
        """
        old_state = self.current_state
        self.person_detected = person_detected
        
        # Track web completion signal
        if web_completed:
            self.web_completion_requested = True
        
        # Track button click
        if button_clicked:
            self.button_clicked = True
        
        # Update interaction time
        if interaction_detected:
            self.last_interaction_time = datetime.now()
            self.is_counting_down = False
            self.countdown_start_time = None
        
        # State machine logic
        if self.current_state == KioskState.STAGE_1_IDLE:
            self._handle_stage_1(person_detected, distance_status)
        
        elif self.current_state == KioskState.STAGE_2_DETECTED:
            self._handle_stage_2(person_detected, distance_status)
        
        elif self.current_state == KioskState.STAGE_3_AUDIO:
            self._handle_stage_3(person_detected, distance_status)
        
        elif self.current_state == KioskState.STAGE_4_WEB:
            self._handle_stage_4(person_detected, distance_status, interaction_detected)
        
        # Check if state changed
        state_changed = (old_state != self.current_state)
        
        if state_changed:
            if self.config.DEVELOPMENT_MODE:
                logger.info(f"State transition: {old_state.value} -> {self.current_state.value}")
            self.previous_state = old_state
            self.state_entry_time = datetime.now()
            
            # Reset timers on state change
            self.very_near_start_time = None
            self.was_very_near = False
            self.far_start_time = None
            self.was_far = False
            self.button_clicked = False
            
            # Reset web completion flag on state change
            if old_state == KioskState.STAGE_4_WEB:
                self.web_completion_requested = False
        
        return state_changed, self.current_state
    
    def _handle_stage_1(self, person_detected, distance_status):
        """
        Stage 1: Idle monitoring with looping welcome animation
        Only transition to Stage 2 when person is at NEAR distance (not FAR)
        """
        if self.config.DEVELOPMENT_MODE:
            logger.info(f"Stage 1: person_detected={person_detected}, distance_status={distance_status}")

        if person_detected and distance_status in ['near', 'very_near']:
            # Person must be at NEAR or closer to trigger audio
            if self.config.DEVELOPMENT_MODE:
                logger.info(f"Stage 1: Person at {distance_status.upper()}, moving to Stage 2")
            self._transition_to(KioskState.STAGE_2_DETECTED)
    
    def _handle_stage_2(self, person_detected, distance_status):
        """
        Stage 2: Person detected at NEAR distance, show hand-waving video+audio (looping)
        
        Transitions:
        - Person moves to VERY_NEAR -> Stage 3 (audio continues but button appears)
        - Person moves to FAR for 8+ seconds -> Back to Stage 1
        - Person disappears for 10+ seconds -> Back to Stage 1
        """
        if not person_detected:
            # Person left completely, start countdown
            if not self.is_counting_down:
                self.is_counting_down = True
                self.countdown_start_time = datetime.now()
                if self.config.DEVELOPMENT_MODE:
                    logger.info(f"Stage 2: Starting {self.config.STAGE2_COUNTDOWN}s countdown (person left)")
            
            # Check if countdown expired
            elapsed = (datetime.now() - self.countdown_start_time).total_seconds()
            if elapsed >= self.config.STAGE2_COUNTDOWN:
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 2: Countdown expired, back to Stage 1")
                self._transition_to(KioskState.STAGE_1_IDLE)
            
            # Reset FAR timer since person is gone
            self.far_start_time = None
            self.was_far = False
        
        elif distance_status == 'very_near':
            # Person very close (<=0.6m), move to stage 3 (button appears, audio continues)
            if self.config.DEVELOPMENT_MODE:
                logger.info("Stage 2: Person very close, moving to Stage 3 (Button appears)")
                logger.info(f"Stage 2: Distance status = {distance_status}, transitioning to STAGE_3_AUDIO")
            self._transition_to(KioskState.STAGE_3_AUDIO)
        
        elif distance_status == 'far':
            # Person is FAR (moved away), track timeout
            if not self.was_far:
                # Just entered FAR zone
                self.far_start_time = datetime.now()
                self.was_far = True
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 2: Person moved to FAR, starting timeout timer")
            
            # Check how long person has been FAR
            time_at_far = (datetime.now() - self.far_start_time).total_seconds()
            
            if self.config.DEVELOPMENT_MODE and int(time_at_far) != int(time_at_far - 0.1):
                logger.info(f"Stage 2: Person at FAR for {time_at_far:.1f}s / {self.config.STAGE2_FAR_TIMEOUT}s")
            
            if time_at_far >= self.config.STAGE2_FAR_TIMEOUT:
                # Person stayed FAR for too long, not interested
                if self.config.DEVELOPMENT_MODE:
                    logger.info(f"Stage 2: Person stayed FAR for {time_at_far:.1f}s, back to Stage 1")
                self._transition_to(KioskState.STAGE_1_IDLE)
        
        else:
            # Person is at NEAR distance (good! still interested)
            # Reset countdown and FAR timer
            if self.is_counting_down:
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 2: Person back at NEAR, resetting countdown")
                self.is_counting_down = False
                self.countdown_start_time = None
            
            if self.was_far:
                # Person moved from FAR to NEAR, reset FAR timer
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 2: Person moved closer (FAR -> NEAR)")
                self.far_start_time = None
                self.was_far = False
    
    def _handle_stage_3(self, person_detected, distance_status):
        """
        Stage 3: Hand-waving video + audio loops continuously + "More Information" button
        User MUST click button to go to Stage 4 (NO AUTO-TRIGGER)
        """
        
        # Priority 1: Check if button was clicked
        if self.button_clicked:
            if self.config.DEVELOPMENT_MODE:
                logger.info("Stage 3: 'More Information' button clicked, opening web")
            self._transition_to(KioskState.STAGE_4_WEB)
            return
        
        if not person_detected:
            # Person left completely, back to stage 1
            if self.config.DEVELOPMENT_MODE:
                logger.info("Stage 3: Person left, back to Stage 1")
            self._transition_to(KioskState.STAGE_1_IDLE)
            return
        
        # Track very_near status for debugging (but DON'T auto-trigger)
        if distance_status == 'very_near':
            # Start timer if JUST entered very_near
            if not self.was_very_near:
                self.very_near_start_time = datetime.now()
                self.was_very_near = True
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 3: Person at VERY_NEAR zone (waiting for button click)")
        else:
            # NOT at very_near anymore
            if self.was_very_near:
                if self.config.DEVELOPMENT_MODE:
                    logger.info(f"Stage 3: Person moved away from VERY_NEAR (now: {distance_status})")
                self.very_near_start_time = None
                self.was_very_near = False
            
            # Check timeout (if person too far for too long)
            time_in_stage = (datetime.now() - self.state_entry_time).total_seconds()
            if distance_status == 'far' and time_in_stage >= self.config.STAGE3_RESPONSE_TIMEOUT:
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 3: Response timeout (user too far), back to Stage 2")
                self._transition_to(KioskState.STAGE_2_DETECTED)
    
    def _handle_stage_4(self, person_detected, distance_status, interaction_detected):
        """
        Stage 4: Web interface active
        Countdown starts if: (Idle timeout) OR (Person moves to NEAR/FAR distance)
        """
        
        # Priority 1: Check if web completion was signaled (button "Selesai 5" clicked)
        if self.web_completion_requested:
            if self.config.DEVELOPMENT_MODE:
                logger.info("Stage 4: Web completion signal received, back to Stage 1")
            self._transition_to(KioskState.STAGE_1_IDLE)
            return
        
        # Priority 2: Check if person moved away to NEAR or FAR
        should_countdown = False
        countdown_reason = ""
        
        if distance_status in ['near', 'far']:
            should_countdown = True
            countdown_reason = f"person moved to {distance_status.upper()} distance"
        
        # Priority 3: Check idle time
        idle_time = (datetime.now() - self.last_interaction_time).total_seconds()
        if idle_time >= self.config.STAGE4_IDLE_TIMEOUT:
            should_countdown = True
            if countdown_reason:
                countdown_reason += " AND idle timeout"
            else:
                countdown_reason = "idle timeout"
        
        if should_countdown:
            # Start countdown
            if not self.is_counting_down:
                self.is_counting_down = True
                self.countdown_start_time = datetime.now()
                if self.config.DEVELOPMENT_MODE:
                    logger.info(f"Stage 4: Starting {self.config.STAGE4_COUNTDOWN_DURATION}s countdown ({countdown_reason})")
            
            # Check if countdown expired
            countdown_elapsed = (datetime.now() - self.countdown_start_time).total_seconds()
            if countdown_elapsed >= self.config.STAGE4_COUNTDOWN_DURATION:
                if self.config.DEVELOPMENT_MODE:
                    logger.info(f"Stage 4: Countdown expired ({countdown_reason}), back to Stage 1")
                self._transition_to(KioskState.STAGE_1_IDLE)
        
        else:
            # User still active and close, reset countdown
            if self.is_counting_down:
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Stage 4: User active again, resetting countdown")
                self.is_counting_down = False
                self.countdown_start_time = None
    
    def _transition_to(self, new_state):
        """Transition to new state and reset timers"""
        self.current_state = new_state
        self.is_counting_down = False
        self.countdown_start_time = None
        self.very_near_start_time = None
        self.was_very_near = False
        self.far_start_time = None
        self.was_far = False
        self.button_clicked = False
    
    def signal_web_completion(self):
        """Called when web interface signals completion (button clicked)"""
        if self.config.DEVELOPMENT_MODE:
            logger.info("Web completion signal received")
        self.web_completion_requested = True
    
    def signal_button_click(self):
        """Called when 'More Information' button is clicked"""
        if self.config.DEVELOPMENT_MODE:
            logger.info("'More Information' button clicked")
        self.button_clicked = True
    
    def get_countdown_remaining(self):
        """Get remaining seconds in current countdown"""
        if not self.is_counting_down or self.countdown_start_time is None:
            return None
        
        elapsed = (datetime.now() - self.countdown_start_time).total_seconds()
        
        if self.current_state == KioskState.STAGE_2_DETECTED:
            remaining = self.config.STAGE2_COUNTDOWN - elapsed
        elif self.current_state == KioskState.STAGE_4_WEB:
            remaining = self.config.STAGE4_COUNTDOWN_DURATION - elapsed
        else:
            remaining = 0
        
        return max(0, remaining)
    
    def get_very_near_duration(self):
        """Get how long person has been at very_near distance (for display)"""
        if self.very_near_start_time is None or not self.was_very_near:
            return 0
        return (datetime.now() - self.very_near_start_time).total_seconds()
    
    def get_far_duration(self):
        """Get how long person has been at FAR distance in Stage 2 (for display)"""
        if self.far_start_time is None or not self.was_far:
            return 0
        return (datetime.now() - self.far_start_time).total_seconds()
    
    def get_state_duration(self):
        """Get how long we've been in current state"""
        return (datetime.now() - self.state_entry_time).total_seconds()
    
    def reset(self):
        """Reset to initial state"""
        logger.info("State Machine RESET")
        self.current_state = KioskState.STAGE_1_IDLE
        self.state_entry_time = datetime.now()
        self.last_interaction_time = datetime.now()
        self.is_counting_down = False
        self.countdown_start_time = None
        self.very_near_start_time = None
        self.was_very_near = False
        self.far_start_time = None
        self.was_far = False
        self.web_completion_requested = False
        self.button_clicked = False