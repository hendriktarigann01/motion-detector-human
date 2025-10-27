"""
State Machine for Kiosk System
Handles 4 stages: IDLE, PERSON_DETECTED, AUDIO_PROMPT, WEB_INTERFACE
"""

from enum import Enum
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        
        # Flags
        self.is_counting_down = False
        self.person_detected = False
        
        logger.info("State Machine initialized at STAGE_1_IDLE")
    
    def update(self, person_detected, distance_status, interaction_detected=False):
        """
        Update state machine based on inputs
        
        Args:
            person_detected (bool): Is person detected by YOLO
            distance_status (str): 'far', 'near', 'very_near'
            interaction_detected (bool): User interaction in Stage 4
        
        Returns:
            tuple: (state_changed, new_state)
        """
        old_state = self.current_state
        self.person_detected = person_detected
        
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
        
        # Check if state changed
        state_changed = (old_state != self.current_state)
        
        if state_changed:
            logger.info(f"State transition: {old_state.value} -> {self.current_state.value}")
            self.previous_state = old_state
            self.state_entry_time = datetime.now()
        
        return state_changed, self.current_state
    
    def _handle_stage_1(self, person_detected, distance_status):
        """Stage 1: Idle monitoring with looping video"""
        if person_detected:
            # Person detected, move to stage 2
            self._transition_to(KioskState.STAGE_2_DETECTED)
    
    def _handle_stage_2(self, person_detected, distance_status):
        """Stage 2: Person detected, show hand-waving video"""
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
            # Person very close (≤0.6m), move to stage 3
            logger.info("Stage 2: Person very close, moving to Stage 3")
            self._transition_to(KioskState.STAGE_3_AUDIO)
        
        else:
            # Person still there but not close enough, reset countdown
            if self.is_counting_down:
                self.is_counting_down = False
                self.countdown_start_time = None
    
    def _handle_stage_3(self, person_detected, distance_status):
        """Stage 3: Audio prompt, waiting for user to get closer"""
        if not person_detected:
            # Person left completely, back to stage 1
            logger.info("Stage 3: Person left, back to Stage 1")
            self._transition_to(KioskState.STAGE_1_IDLE)
        
        elif distance_status == 'very_near':
            # Person still very close, move to web interface
            logger.info("Stage 3: Person confirmed close, moving to Stage 4")
            self._transition_to(KioskState.STAGE_4_WEB)
        
        elif distance_status == 'far':
            # Person moved away, check timeout
            time_in_stage = (datetime.now() - self.state_entry_time).total_seconds()
            if time_in_stage >= self.config.STAGE3_RESPONSE_TIMEOUT:
                logger.info("Stage 3: Response timeout, back to Stage 2")
                self._transition_to(KioskState.STAGE_2_DETECTED)
    
    def _handle_stage_4(self, person_detected, interaction_detected):
        """Stage 4: Web interface active"""
        # Check idle time
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
                logger.info("Stage 4: Final countdown expired, resetting to Stage 1")
                self._transition_to(KioskState.STAGE_1_IDLE)
        
        else:
            # User still active, reset countdown
            if self.is_counting_down:
                self.is_counting_down = False
                self.countdown_start_time = None
    
    def _transition_to(self, new_state):
        """Transition to new state and reset timers"""
        self.current_state = new_state
        self.is_counting_down = False
        self.countdown_start_time = None
    
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