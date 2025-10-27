"""
Web Interface Handler
Opens browser in fullscreen/kiosk mode and monitors interaction
"""

import webbrowser
import logging
from datetime import datetime
import threading
import time

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("PyAutoGUI not available. Mouse tracking will be disabled.")

logger = logging.getLogger(__name__)


class WebInterfaceHandler:
    """Manages web browser for catalog display"""
    
    def __init__(self, config):
        self.config = config
        self.is_active = False
        self.last_mouse_pos = None
        self.last_interaction_time = None
        self.monitoring_thread = None
        self.should_monitor = False
    
    def open_browser(self):
        """Open web browser in fullscreen/kiosk mode"""
        try:
            logger.info(f"Opening browser: {self.config.WEB_URL}")
            
            # Open URL in default browser
            # For production, you might want to use specific browser flags:
            # - Chrome: --kiosk --fullscreen
            # - Firefox: -kiosk
            webbrowser.open(self.config.WEB_URL, new=2)  # new=2 opens in new tab
            
            self.is_active = True
            self.last_interaction_time = datetime.now()
            self.last_mouse_pos = pyautogui.position()
            
            # Start monitoring interaction in background
            self._start_monitoring()
            
            # Optional: Auto-fullscreen after a delay
            time.sleep(2)  # Wait for browser to open
            if self.config.FULLSCREEN_MODE:
                pyautogui.press('f11')  # F11 for fullscreen in most browsers
            
            logger.info("Browser opened successfully")
        
        except Exception as e:
            logger.error(f"Error opening browser: {e}")
            self.is_active = False
    
    def _start_monitoring(self):
        """Start background thread to monitor mouse/touch interaction"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.should_monitor = True
        self.monitoring_thread = threading.Thread(target=self._monitor_interaction, daemon=True)
        self.monitoring_thread.start()
        logger.info("Started interaction monitoring")
    
    def _monitor_interaction(self):
        """Monitor mouse movement and clicks (runs in background thread)"""
        while self.should_monitor and self.is_active:
            try:
                current_pos = pyautogui.position()
                
                # Check if mouse moved
                if self.last_mouse_pos != current_pos:
                    self.last_interaction_time = datetime.now()
                    self.last_mouse_pos = current_pos
                
                time.sleep(0.1)  # Check every 100ms
            
            except Exception as e:
                logger.error(f"Error in interaction monitoring: {e}")
                break
    
    def check_interaction(self):
        """
        Check if user has interacted recently
        
        Returns:
            bool: True if interaction detected recently
        """
        if not self.is_active or self.last_interaction_time is None:
            return False
        
        idle_time = (datetime.now() - self.last_interaction_time).total_seconds()
        return idle_time < 1.0  # Consider interaction if within last second
    
    def close_browser(self):
        """Close browser and stop monitoring"""
        logger.info("Closing browser")
        self.is_active = False
        self.should_monitor = False
        
        # Stop monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        
        # Close browser window (platform dependent)
        try:
            # Alt+F4 works on Windows/Linux
            pyautogui.hotkey('alt', 'f4')
        except Exception as e:
            logger.warning(f"Could not close browser automatically: {e}")
    
    def reset(self):
        """Reset handler state"""
        self.close_browser()
        self.last_mouse_pos = None
        self.last_interaction_time = None


# Alternative: Embedded browser using PyQt5 or Tkinter
# Uncomment below if you want embedded browser instead of system browser

"""
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer

class EmbeddedBrowser(QMainWindow):
    def __init__(self, url, fullscreen=True):
        super().__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)
        
        if fullscreen:
            self.showFullScreen()
        else:
            self.show()
    
    def get_interaction_time(self):
        # Track mouse movement, clicks, etc.
        pass
"""