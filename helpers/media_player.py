"""
Media Player for handling video and audio playback
"""

import cv2
import pygame
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MediaPlayer:
    """Handles video and audio playback for kiosk"""
    
    def __init__(self, config):
        self.config = config
        
        # Video players
        self.idle_video = None
        self.waving_video = None
        self.current_video = None
        self.current_video_name = None
        
        # Audio
        pygame.mixer.init()
        self.audio_playing = False
        
        # Fade effect
        self.fade_alpha = 1.0
        self.is_fading = False
        self.fade_direction = 0  # -1 for fade out, 1 for fade in
        
        self._load_media()
    
    def _load_media(self):
        """Load all media files"""
        try:
            # Load idle video
            if Path(self.config.VIDEO_IDLE_LOOP).exists():
                self.idle_video = cv2.VideoCapture(self.config.VIDEO_IDLE_LOOP)
                logger.info(f"Loaded idle video: {self.config.VIDEO_IDLE_LOOP}")
            else:
                logger.warning(f"Idle video not found: {self.config.VIDEO_IDLE_LOOP}")
            
            # Load hand waving video
            if Path(self.config.VIDEO_HAND_WAVING).exists():
                self.waving_video = cv2.VideoCapture(self.config.VIDEO_HAND_WAVING)
                logger.info(f"Loaded waving video: {self.config.VIDEO_HAND_WAVING}")
            else:
                logger.warning(f"Waving video not found: {self.config.VIDEO_HAND_WAVING}")
            
            # Load audio
            if Path(self.config.AUDIO_SPEECH).exists():
                pygame.mixer.music.load(self.config.AUDIO_SPEECH)
                logger.info(f"Loaded audio: {self.config.AUDIO_SPEECH}")
            else:
                logger.warning(f"Audio not found: {self.config.AUDIO_SPEECH}")
        
        except Exception as e:
            logger.error(f"Error loading media: {e}")
    
    def play_idle_video(self):
        """Start playing idle looping video"""
        if self.current_video_name != 'idle':
            logger.info("Starting idle video")
            self.current_video = self.idle_video
            self.current_video_name = 'idle'
            if self.current_video:
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.stop_audio()
    
    def play_waving_video(self):
        """Start playing hand waving video"""
        if self.current_video_name != 'waving':
            logger.info("Starting hand waving video")
            self.current_video = self.waving_video
            self.current_video_name = 'waving'
            if self.current_video:
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.stop_audio()
    
    def play_audio(self):
        """Play speech audio (looping)"""
        if not self.audio_playing:
            try:
                pygame.mixer.music.play(-1)  # -1 = loop indefinitely
                self.audio_playing = True
                logger.info("Started audio playback")
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
    
    def stop_audio(self):
        """Stop audio playback"""
        if self.audio_playing:
            pygame.mixer.music.stop()
            self.audio_playing = False
            logger.info("Stopped audio playback")
    
    def get_video_frame(self, target_size=None):
        """
        Get current video frame
        
        Args:
            target_size: (width, height) to resize frame, or None
        
        Returns:
            numpy array (BGR image) or None
        """
        if self.current_video is None or not self.current_video.isOpened():
            return None
        
        ret, frame = self.current_video.read()
        
        if not ret:
            # Loop video
            self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.current_video.read()
            
            if not ret:
                return None
        
        # Resize if needed
        if target_size:
            frame = cv2.resize(frame, target_size)
        
        # Apply fade effect
        if self.fade_alpha < 1.0:
            overlay = np.zeros_like(frame)
            frame = cv2.addWeighted(frame, self.fade_alpha, overlay, 1 - self.fade_alpha, 0)
        
        return frame
    
    def start_fade_out(self):
        """Start fade out effect"""
        self.is_fading = True
        self.fade_direction = -1
        self.fade_alpha = 1.0
        logger.info("Starting fade out")
    
    def start_fade_in(self):
        """Start fade in effect"""
        self.is_fading = True
        self.fade_direction = 1
        self.fade_alpha = 0.0
        logger.info("Starting fade in")
    
    def update_fade(self, delta_time):
        """
        Update fade effect
        
        Args:
            delta_time: Time since last update (seconds)
        
        Returns:
            bool: True if fade is complete
        """
        if not self.is_fading:
            return True
        
        # Calculate fade speed
        fade_speed = 1.0 / self.config.FADE_DURATION
        
        # Update alpha
        self.fade_alpha += self.fade_direction * fade_speed * delta_time
        
        # Clamp alpha
        self.fade_alpha = max(0.0, min(1.0, self.fade_alpha))
        
        # Check if fade complete
        if self.fade_direction == -1 and self.fade_alpha <= 0.0:
            self.is_fading = False
            return True
        elif self.fade_direction == 1 and self.fade_alpha >= 1.0:
            self.is_fading = False
            return True
        
        return False
    
    def stop_all(self):
        """Stop all media playback"""
        self.stop_audio()
        self.current_video = None
        self.current_video_name = None
    
    def cleanup(self):
        """Release all resources"""
        logger.info("Cleaning up media player")
        self.stop_audio()
        
        if self.idle_video:
            self.idle_video.release()
        if self.waving_video:
            self.waving_video.release()
        
        pygame.mixer.quit()