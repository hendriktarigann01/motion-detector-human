"""
Web Interface Handler
Opens browser and monitors interaction + completion signal
"""

import webbrowser
import logging
from datetime import datetime
import threading
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("PyAutoGUI not available. Mouse tracking will be disabled.")

logger = logging.getLogger(__name__)


class CompletionSignalHandler(SimpleHTTPRequestHandler):
    """HTTP handler to receive completion signals from web interface"""
    
    completion_callback = None
    
    def do_POST(self):
        """Handle POST requests from web interface"""
        if self.path == '/complete':
            # Signal received from web
            logger.info("Received completion signal from web interface")
            if CompletionSignalHandler.completion_callback:
                CompletionSignalHandler.completion_callback()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


class WebInterfaceHandler:
    """Manages web browser for catalog display"""
    
    def __init__(self, config):
        self.config = config
        self.is_active = False
        self.last_mouse_pos = None
        self.last_interaction_time = None
        self.monitoring_thread = None
        self.should_monitor = False
        
        # Completion signal handling
        self.completion_received = False
        self.signal_server = None
        self.signal_thread = None
        
        # Start signal server
        self._start_signal_server()
    
    def _start_signal_server(self):
        """Start HTTP server to receive completion signals"""
        try:
            CompletionSignalHandler.completion_callback = self._on_completion_signal
            self.signal_server = HTTPServer(('localhost', 8765), CompletionSignalHandler)
            self.signal_thread = threading.Thread(target=self.signal_server.serve_forever, daemon=True)
            self.signal_thread.start()
            logger.info("Completion signal server started on http://localhost:8765")
        except Exception as e:
            logger.error(f"Failed to start signal server: {e}")
    
    def _on_completion_signal(self):
        """Called when completion signal received from web"""
        self.completion_received = True
        logger.info("Completion signal set")
    
    def open_browser(self):
        """Open web browser in fullscreen/kiosk mode"""
        try:
            logger.info(f"Opening browser: {self.config.WEB_URL}")
            
            # Reset completion flag
            self.completion_received = False
            
            # Open URL in default browser
            webbrowser.open(self.config.WEB_URL, new=2)
            
            self.is_active = True
            self.last_interaction_time = datetime.now()
            
            if PYAUTOGUI_AVAILABLE:
                self.last_mouse_pos = pyautogui.position()
            
            # Start monitoring interaction in background
            self._start_monitoring()
            
            # Auto-fullscreen after delay
            time.sleep(2)
            if self.config.FULLSCREEN_MODE and PYAUTOGUI_AVAILABLE:
                try:
                    pyautogui.press('f11')
                except:
                    pass
            
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
                if PYAUTOGUI_AVAILABLE:
                    current_pos = pyautogui.position()
                    
                    # Check if mouse moved
                    if self.last_mouse_pos != current_pos:
                        self.last_interaction_time = datetime.now()
                        self.last_mouse_pos = current_pos
                
                time.sleep(0.1)
            
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
        return idle_time < 1.0
    
    def check_completion(self):
        """
        Check if web interface signaled completion
        
        Returns:
            bool: True if completion signal received
        """
        return self.completion_received
    
    def close_browser(self):
        """Close browser and stop monitoring"""
        logger.info("Closing browser")
        self.is_active = False
        self.should_monitor = False
        self.completion_received = False
        
        # Stop monitoring thread
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        
        # Close browser window
        if PYAUTOGUI_AVAILABLE:
            try:
                pyautogui.hotkey('alt', 'f4')
            except Exception as e:
                logger.warning(f"Could not close browser: {e}")
    
    def reset(self):
        """Reset handler state"""
        self.close_browser()
        self.last_mouse_pos = None
        self.last_interaction_time = None
        self.completion_received = False
    
    def cleanup(self):
        """Cleanup resources"""
        self.close_browser()
        if self.signal_server:
            self.signal_server.shutdown()