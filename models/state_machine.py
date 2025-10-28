"""
State Machine for Kiosk System
Handles 5 stages: IDLE, PERSON_DETECTED, AUDIO_PROMPT, WEB_INTERFACE, THANK_YOU
FIXED: Stage 3 requires 3 continuous seconds at very_near before opening web
"""

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
    STAGE_5_THANKYOU = "thank_you_video"


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
        
        # FIXED: Add separate timer for very_near stability check
        self.very_near_start_time = None
        self.was_very_near = False
        
        # Flags
        self.is_counting_down = False
        self.person_detected = False
        self.web_completion_requested = False
        
        logger.info("State Machine initialized at STAGE_1_IDLE")
    
    def update(self, person_detected, distance_status, interaction_detected=False, web_completed=False):
        """
        Update state machine based on inputs
        
        Args:
            person_detected (bool): Is person detected by YOLO
            distance_status (str): 'far', 'near', 'very_near'
            interaction_detected (bool): User interaction in Stage 4
            web_completed (bool): Web signals button "Selesai 5" clicked
        
        Returns:
            tuple: (state_changed, new_state)
        """
        old_state = self.current_state
        self.person_detected = person_detected
        
        # Track web completion signal
        if web_completed:
            self.web_completion_requested = True
        
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
            self._handle_stage_4(person_detected, interaction_detected)
        
        elif self.current_state == KioskState.STAGE_5_THANKYOU:
            self._handle_stage_5()
        
        # Check if state changed
        state_changed = (old_state != self.current_state)
        
        if state_changed:
            logger.info(f"State transition: {old_state.value} -> {self.current_state.value}")
            self.previous_state = old_state
            self.state_entry_time = datetime.now()
            
            # FIXED: Reset timers on state change
            self.very_near_start_time = None
            self.was_very_near = False
            
            # Reset web completion flag on state change
            if old_state == KioskState.STAGE_4_WEB:
                self.web_completion_requested = False
        
        return state_changed, self.current_state
    
    def _handle_stage_1(self, person_detected, distance_status):
        """Stage 1: Idle monitoring with looping video"""
        if person_detected:
            self._transition_to(KioskState.STAGE_2_DETECTED)
    
    def _handle_stage_2(self, person_detected, distance_status):
        """Stage 2: Person detected, show hand-waving video (looping)"""
        if not person_detected:
            # Person left, start countdown
            if not self.is_counting_down:
                self.is_counting_down = True
                self.countdown_start_time = datetime.now()
                logger.info(f"Stage 2: Starting {self.config.STAGE2_COUNTDOWN}s countdown")
            
            # Check if countdown expired
            elapsed = (datetime.now() - self.countdown_start_time).total_seconds()
            if elapsed >= self.config.STAGE2_COUNTDOWN:
                logger.info("Stage 2: Countdown expired, back to Stage 1")
                self._transition_to(KioskState.STAGE_1_IDLE)
        
        elif distance_status == 'very_near':
            # Person very close (≤0.6m), move to stage 3 (audio)
            logger.info("Stage 2: Person very close, moving to Stage 3 (Audio)")
            self._transition_to(KioskState.STAGE_3_AUDIO)
        
        else:
            # Person still there but not close enough, reset countdown
            if self.is_counting_down:
                self.is_counting_down = False
                self.countdown_start_time = None
    
    def _handle_stage_3(self, person_detected, distance_status):
        """
        Stage 3: Audio prompt (woman-speech.mp3) loops continuously
        FIXED: User MUST stay at very_near distance for 3 CONTINUOUS seconds to trigger Stage 4
        """
        if not person_detected:
            # Person left completely, back to stage 1
            logger.info("Stage 3: Person left, back to Stage 1")
            self._transition_to(KioskState.STAGE_1_IDLE)
            return
        
        # FIXED: Track CONTINUOUS very_near time
        if distance_status == 'very_near':
            # Start timer if JUST entered very_near
            if not self.was_very_near:
                self.very_near_start_time = datetime.now()
                self.was_very_near = True
                logger.info("Stage 3: Person entered VERY_NEAR zone, starting 3s stability timer")
            
            # Check how long we've been CONTINUOUSLY at very_near
            if self.very_near_start_time is not None:
                time_at_very_near = (datetime.now() - self.very_near_start_time).total_seconds()
                
                # Log progress (every 0.5s to avoid spam)
                if int(time_at_very_near * 2) != int((time_at_very_near - 0.1) * 2):
                    logger.info(f"Stage 3: Stable at VERY_NEAR for {time_at_very_near:.1f}s / 3.0s")
                
                # MUST be stable for 3 continuous seconds
                if time_at_very_near >= 3.0:
                    logger.info(f"✅ Stage 3: Person STABLE at VERY_NEAR for {time_at_very_near:.1f}s, opening web")
                    self._transition_to(KioskState.STAGE_4_WEB)
        
        else:
            # NOT at very_near anymore - RESET timer immediately
            if self.was_very_near:
                logger.info(f"⚠️ Stage 3: Person moved away from VERY_NEAR (now: {distance_status}), RESETTING timer")
                self.very_near_start_time = None
                self.was_very_near = False
            
            # Check timeout (if person too far for too long)
            time_in_stage = (datetime.now() - self.state_entry_time).total_seconds()
            if distance_status == 'far' and time_in_stage >= self.config.STAGE3_RESPONSE_TIMEOUT:
                logger.info("Stage 3: Response timeout (user too far), back to Stage 2")
                self._transition_to(KioskState.STAGE_2_DETECTED)
    
    def _handle_stage_4(self, person_detected, interaction_detected):
        """Stage 4: Web interface active, wait for completion signal or timeout"""
        
        # Priority 1: Check if web completion was signaled (button "Selesai 5" clicked)
        if self.web_completion_requested:
            logger.info("Stage 4: Web completion signal received, moving to Thank You")
            self._transition_to(KioskState.STAGE_5_THANKYOU)
            return
        
        # Priority 2: Check idle time
        idle_time = (datetime.now() - self.last_interaction_time).total_seconds()
        
        if idle_time >= self.config.STAGE4_IDLE_TIMEOUT:
            # Start final countdown
            if not self.is_counting_down:
                self.is_counting_down = True
                self.countdown_start_time = datetime.now()
                logger.info(f"Stage 4: Starting final {self.config.STAGE4_COUNTDOWN_DURATION}s countdown")
            
            # Check if countdown expired
            countdown_elapsed = (datetime.now() - self.countdown_start_time).total_seconds()
            if countdown_elapsed >= self.config.STAGE4_COUNTDOWN_DURATION:
                logger.info("Stage 4: Countdown expired, moving to Thank You")
                self._transition_to(KioskState.STAGE_5_THANKYOU)
        
        else:
            # User still active, reset countdown
            if self.is_counting_down:
                self.is_counting_down = False
                self.countdown_start_time = None
    
    def _handle_stage_5(self):
        """
        Stage 5: Thank you video (plays once, no loop)
        Transition handled by main.py when video finishes
        """
        pass
    
    def _transition_to(self, new_state):
        """Transition to new state and reset timers"""
        self.current_state = new_state
        self.is_counting_down = False
        self.countdown_start_time = None
        self.very_near_start_time = None
        self.was_very_near = False
    
    def signal_web_completion(self):
        """Called when web interface signals completion (button clicked)"""
        logger.info("Web completion signal received")
        self.web_completion_requested = True
    
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
        self.web_completion_requested = False