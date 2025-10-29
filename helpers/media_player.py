"""
Media Player for handling video and audio playback
UPDATED: Welcome animation (Stage 1), Hand-waving video+audio (Stage 2 & 3)
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
        self.welcome_video = None
        self.handwaving_video = None
        self.current_video = None
        self.current_video_name = None
        
        # Audio (for separate audio files)
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            logger.info("Pygame mixer initialized")
        except Exception as e:
            logger.error(f"Failed to init pygame mixer: {e}")
        
        self.audio_playing = False
        
        self._load_media()
    
    def _load_media(self):
        """Load all media files"""
        try:
            # Load welcome animation (Stage 1)
            welcome_path = Path(self.config.WELCOME_ANIMATION)
            if welcome_path.exists():
                self.welcome_video = cv2.VideoCapture(str(welcome_path))
                if self.welcome_video.isOpened():
                    logger.info(f"✅ Loaded welcome animation: {welcome_path}")
                else:
                    logger.error(f"❌ Failed to open welcome animation: {welcome_path}")
                    self.welcome_video = None
            else:
                logger.error(f"❌ Welcome animation not found: {welcome_path}")
            
            # Load hand waving video (Stage 2 & 3)
            handwaving_path = Path(self.config.VIDEO_HAND_WAVING)
            if handwaving_path.exists():
                self.handwaving_video = cv2.VideoCapture(str(handwaving_path))
                if self.handwaving_video.isOpened():
                    logger.info(f"✅ Loaded hand-waving video: {handwaving_path}")
                else:
                    logger.error(f"❌ Failed to open hand-waving video: {handwaving_path}")
                    self.handwaving_video = None
            else:
                logger.error(f"❌ Hand-waving video not found: {handwaving_path}")
            
            # Load hand waving audio (Stage 2 & 3)
            audio_path = Path(self.config.AUDIO_HAND_WAVING)
            if audio_path.exists():
                try:
                    pygame.mixer.music.load(str(audio_path))
                    logger.info(f"✅ Loaded hand-waving audio: {audio_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to load hand-waving audio: {e}")
            else:
                logger.error(f"❌ Hand-waving audio not found: {audio_path}")
        
        except Exception as e:
            logger.error(f"Error loading media: {e}")
    
    def play_welcome_animation(self):
        """Start playing welcome animation (looping) - Stage 1"""
        if self.current_video_name != 'welcome':
            logger.info("▶️ Starting welcome animation")
            self.current_video = self.welcome_video
            self.current_video_name = 'welcome'
            if self.current_video and self.current_video.isOpened():
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                logger.error("Welcome animation not available!")
            self.stop_audio()
    
    def play_handwaving_video_and_audio(self):
        """Start playing hand-waving video + audio (both looping) - Stage 2 & 3"""
        if self.current_video_name != 'handwaving':
            logger.info("▶️ Starting hand-waving video + audio")
            self.current_video = self.handwaving_video
            self.current_video_name = 'handwaving'
            if self.current_video and self.current_video.isOpened():
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                logger.error("Hand-waving video not available!")
            
            # Start audio looping
            self.play_audio_loop()
    
    def play_audio_loop(self):
        """Play hand-waving audio (looping)"""
        if not self.audio_playing:
            try:
                pygame.mixer.music.play(-1)  # -1 = loop indefinitely
                self.audio_playing = True
                logger.info("🔊 Started audio playback (looping)")
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
    
    def stop_audio(self):
        """Stop audio playback"""
        if self.audio_playing:
            try:
                pygame.mixer.music.stop()
                self.audio_playing = False
                logger.info("🔇 Stopped audio playback")
            except Exception as e:
                logger.error(f"Error stopping audio: {e}")
    
    def get_video_frame(self, target_size=None, loop=True):
        """
        Get current video frame (OPTIMIZED)
        
        Args:
            target_size: (width, height) to resize frame, or None
            loop: If True, loop video. If False, stop at end
        
        Returns:
            numpy array (BGR image) or None
        """
        if self.current_video is None or not self.current_video.isOpened():
            logger.error(f"Current video not available: {self.current_video_name}")
            return None
        
        ret, frame = self.current_video.read()
        
        if not ret:
            # Video ended
            if loop:
                # Loop video
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.current_video.read()
            else:
                # Don't loop
                return None
            
            if not ret:
                logger.error(f"Failed to read frame from {self.current_video_name}")
                return None
        
        # Resize if needed (FAST resize method)
        if target_size:
            frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
        
        return frame
    
    def stop_all(self):
        """Stop all media playback"""
        self.stop_audio()
    
    def cleanup(self):
        """Release all resources"""
        logger.info("Cleaning up media player")
        self.stop_audio()
        
        if self.welcome_video:
            self.welcome_video.release()
        if self.handwaving_video:
            self.handwaving_video.release()
        
        try:
            pygame.mixer.quit()
        except:
            pass