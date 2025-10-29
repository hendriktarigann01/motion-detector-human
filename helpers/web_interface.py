"""
Web Interface Handler for Kiosk
UPDATED: Auto fullscreen (F11) when browser opens
Handles browser automation, interaction tracking, and completion signals
"""

import logging
import time
from datetime import datetime
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not installed. Web interface features will be disabled.")
    logger.warning("Install with: pip install selenium")


class WebInterfaceHandler:
    """Handles web browser automation for kiosk interface"""
    
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.is_browser_open = False
        self.last_interaction_time = datetime.now()
        self.completion_signaled = False
        
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available - web interface disabled")
            return
        
        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--disable-notifications')
        self.chrome_options.add_argument('--disable-popup-blocking')
        # Disable automation flags
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        logger.info("Web Interface Handler initialized")
    
    def open_browser(self):
        """Open browser and navigate to web interface with auto fullscreen"""
        if not SELENIUM_AVAILABLE:
            logger.error("Cannot open browser - Selenium not available")
            return False
        
        try:
            if self.is_browser_open and self.driver:
                logger.warning("Browser already open")
                return True
            
            if self.config.DEVELOPMENT_MODE:
                logger.info("Opening web browser...")
            
            # Initialize Chrome driver
            self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Navigate to URL
            self.driver.get(self.config.WEB_URL)
            if self.config.DEVELOPMENT_MODE:
                logger.info(f"Navigated to: {self.config.WEB_URL}")
            
            # Wait for page to load
            time.sleep(1)
            
            # AUTO FULLSCREEN: Press F11
            try:
                body = self.driver.find_element(By.TAG_NAME, 'body')
                body.send_keys(Keys.F11)
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Auto fullscreen (F11) activated")
            except Exception as e:
                logger.warning(f"Failed to auto fullscreen: {e}")
            
            self.is_browser_open = True
            self.last_interaction_time = datetime.now()
            self.completion_signaled = False
            
            # Start monitoring thread
            self._start_monitoring()
            
            if self.config.DEVELOPMENT_MODE:
                logger.info("Web browser opened successfully (fullscreen)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
            self.driver = None
            self.is_browser_open = False
            return False
    
    def close_browser(self):
        """Close browser window"""
        if not self.is_browser_open or not self.driver:
            return
        
        try:
            if self.config.DEVELOPMENT_MODE:
                logger.info("Closing web browser...")
            self.driver.quit()
            self.driver = None
            self.is_browser_open = False
            if self.config.DEVELOPMENT_MODE:
                logger.info("Browser closed successfully")
        
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            self.driver = None
            self.is_browser_open = False
    
    def check_interaction(self):
        """
        Check if user is interacting with web interface
        Returns True if interaction detected recently
        """
        if not self.is_browser_open or not self.driver:
            return False
        
        try:
            # Check if window is still active
            current_url = self.driver.current_url
            
            # Check for mouse movement or clicks (via JavaScript)
            last_activity = self.driver.execute_script("""
                return window.lastActivityTime || 0;
            """)
            
            # If we got activity timestamp, check if it's recent
            if last_activity and isinstance(last_activity, (int, float)):
                current_time = time.time() * 1000  # Convert to ms
                time_since_activity = (current_time - last_activity) / 1000  # Convert to seconds
                
                if time_since_activity < self.config.MOUSE_IDLE_THRESHOLD:
                    self.last_interaction_time = datetime.now()
                    return True
            
            # Check if we have recent interaction
            time_since_last = (datetime.now() - self.last_interaction_time).total_seconds()
            return time_since_last < self.config.MOUSE_IDLE_THRESHOLD
        
        except Exception as e:
            if self.config.DEVELOPMENT_MODE:
                logger.error(f"Error checking interaction: {e}")
            return False
    
    def check_completion(self):
        """
        Check if web interface has signaled completion
        Returns True if 'Selesai 5' button was clicked
        """
        if not self.is_browser_open or not self.driver:
            return False
        
        if self.completion_signaled:
            return True
        
        try:
            # Check for completion flag (set by web app)
            completion_flag = self.driver.execute_script("""
                return window.kioskCompleted || false;
            """)
            
            if completion_flag:
                if self.config.DEVELOPMENT_MODE:
                    logger.info("Web completion signal detected!")
                self.completion_signaled = True
                return True
            
            return False
        
        except Exception as e:
            if self.config.DEVELOPMENT_MODE:
                logger.error(f"Error checking completion: {e}")
            return False
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        # Inject activity tracking script
        try:
            self.driver.execute_script("""
                window.lastActivityTime = Date.now();
                
                // Track mouse movement
                document.addEventListener('mousemove', function() {
                    window.lastActivityTime = Date.now();
                });
                
                // Track clicks
                document.addEventListener('click', function() {
                    window.lastActivityTime = Date.now();
                });
                
                // Track touch events
                document.addEventListener('touchstart', function() {
                    window.lastActivityTime = Date.now();
                });
                
                // Track scrolling
                document.addEventListener('scroll', function() {
                    window.lastActivityTime = Date.now();
                });
            """)
            
            if self.config.DEVELOPMENT_MODE:
                logger.info("Activity tracking script injected")
        
        except Exception as e:
            logger.error(f"Failed to inject tracking script: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        self.close_browser()


# Fallback class when Selenium is not available
class WebInterfaceHandlerFallback:
    """Fallback handler when Selenium is not installed"""
    
    def __init__(self, config):
        self.config = config
        self.is_browser_open = False
        logger.warning("Using fallback web interface handler (Selenium not available)")
    
    def open_browser(self):
        logger.warning("Cannot open browser - Selenium not installed")
        return False
    
    def close_browser(self):
        pass
    
    def check_interaction(self):
        return False
    
    def check_completion(self):
        return False
    
    def cleanup(self):
        pass


# Use fallback if Selenium is not available
if not SELENIUM_AVAILABLE:
    WebInterfaceHandler = WebInterfaceHandlerFallback