"""
Media Player for handling video and audio playback
FIXED: Video loading, audio in video, performance
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
        self.thankyou_video = None
        self.current_video = None
        self.current_video_name = None
        
        # Video info
        self.thankyou_has_audio = False
        
        # Audio (for separate audio files only)
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
            # Load idle video
            idle_path = Path(self.config.VIDEO_IDLE_LOOP)
            if idle_path.exists():
                self.idle_video = cv2.VideoCapture(str(idle_path))
                if self.idle_video.isOpened():
                    logger.info(f"Loaded idle video: {idle_path}")
                else:
                    logger.error(f"Failed to open idle video: {idle_path}")
                    self.idle_video = None
            else:
                logger.error(f"Idle video not found: {idle_path}")
            
            # Load hand waving video
            waving_path = Path(self.config.VIDEO_HAND_WAVING)
            if waving_path.exists():
                self.waving_video = cv2.VideoCapture(str(waving_path))
                if self.waving_video.isOpened():
                    logger.info(f"Loaded waving video: {waving_path}")
                else:
                    logger.error(f"Failed to open waving video: {waving_path}")
                    self.waving_video = None
            else:
                logger.error(f"Waving video not found: {waving_path}")
            
            # Load thank you video (with audio check)
            thankyou_path = Path(self.config.VIDEO_THANK_YOU)
            if thankyou_path.exists():
                self.thankyou_video = cv2.VideoCapture(str(thankyou_path))
                if self.thankyou_video.isOpened():
                    # Check if video has audio
                    # OpenCV doesn't directly support audio, we need pygame for that
                    logger.info(f"Loaded thank you video: {thankyou_path}")
                    logger.warning("OpenCV doesn't play video audio. Use pygame or vlc for audio support.")
                    
                    # Try to play audio using pygame if possible
                    try:
                        # Convert video to audio if needed, or use separate audio file
                        # For now, just flag it
                        self.thankyou_has_audio = True
                    except:
                        pass
                else:
                    logger.error(f"Failed to open thank you video: {thankyou_path}")
                    self.thankyou_video = None
            else:
                logger.error(f"Thank you video not found: {thankyou_path}")
            
            # Load separate audio file (woman-speech.mp3)
            audio_path = Path(self.config.AUDIO_SPEECH)
            if audio_path.exists():
                try:
                    pygame.mixer.music.load(str(audio_path))
                    logger.info(f"Loaded audio: {audio_path}")
                except Exception as e:
                    logger.error(f"Failed to load audio: {e}")
            else:
                logger.error(f"Audio not found: {audio_path}")
        
        except Exception as e:
            logger.error(f"Error loading media: {e}")
    
    def play_idle_video(self):
        """Start playing idle looping video"""
        if self.current_video_name != 'idle':
            logger.info("Starting idle video")
            self.current_video = self.idle_video
            self.current_video_name = 'idle'
            if self.current_video and self.current_video.isOpened():
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                logger.error("Idle video not available!")
            self.stop_audio()
    
    def play_waving_video(self):
        """Start playing hand waving video"""
        if self.current_video_name != 'waving':
            logger.info("Starting hand waving video")
            self.current_video = self.waving_video
            self.current_video_name = 'waving'
            if self.current_video and self.current_video.isOpened():
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                logger.error("Waving video not available!")
            self.stop_audio()
    
    def play_thankyou_video(self):
        """Start playing thank you video (one-time, no loop) + audio"""
        if self.current_video_name != 'thankyou':
            logger.info("Starting thank you video")
            self.current_video = self.thankyou_video
            self.current_video_name = 'thankyou'
            if self.current_video and self.current_video.isOpened():
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                logger.error("Thank you video not available!")
            
            # Stop any previous audio
            self.stop_audio()
            
            # FIXED: Play thank you audio (separate file)
            if hasattr(self.config, 'AUDIO_THANK_YOU'):
                audio_path = Path(self.config.AUDIO_THANK_YOU)
                if audio_path.exists():
                    try:
                        pygame.mixer.music.load(str(audio_path))
                        pygame.mixer.music.play(0)  # Play once (0 = no loop)
                        self.audio_playing = True
                        logger.info("Playing thank you audio")
                    except Exception as e:
                        logger.error(f"Failed to play thank you audio: {e}")
                else:
                    logger.warning(f"Thank you audio not found: {audio_path}")
            else:
                logger.warning("AUDIO_THANK_YOU not configured")
    
    def play_audio(self):
        """Play speech audio (looping)"""
        if not self.audio_playing:
            try:
                pygame.mixer.music.play(-1)  # -1 = loop indefinitely
                self.audio_playing = True
                logger.info("Started audio playback (looping)")
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
    
    def stop_audio(self):
        """Stop audio playback"""
        if self.audio_playing:
            try:
                pygame.mixer.music.stop()
                self.audio_playing = False
                logger.info("Stopped audio playback")
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
            if loop and self.current_video_name != 'thankyou':
                # Loop video
                self.current_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.current_video.read()
            else:
                # Don't loop (thank you video plays once)
                return None
            
            if not ret:
                logger.error(f"Failed to read frame from {self.current_video_name}")
                return None
        
        # Resize if needed (FAST resize method)
        if target_size:
            frame = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
        
        return frame
    
    def is_video_finished(self):
        """Check if current video has finished (for non-looping videos)"""
        if self.current_video is None or not self.current_video.isOpened():
            return True
        
        if self.current_video_name == 'thankyou':
            # Check if we've reached the end
            current_frame = self.current_video.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.current_video.get(cv2.CAP_PROP_FRAME_COUNT)
            
            if total_frames <= 0:
                return True
            
            finished = current_frame >= total_frames - 2  # -2 for safety margin
            if finished:
                logger.info(f"Thank you video finished (frame {current_frame}/{total_frames})")
            return finished
        
        return False
    
    def stop_all(self):
        """Stop all media playback"""
        self.stop_audio()
        # Don't set current_video to None, just stop audio
    
    def cleanup(self):
        """Release all resources"""
        logger.info("Cleaning up media player")
        self.stop_audio()
        
        if self.idle_video:
            self.idle_video.release()
        if self.waving_video:
            self.waving_video.release()
        if self.thankyou_video:
            self.thankyou_video.release()
        
        try:
            pygame.mixer.quit()
        except:
            pass