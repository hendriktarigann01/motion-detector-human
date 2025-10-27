"""
YOLO Person Detection with Distance Estimation
"""

import torch
import cv2
import numpy as np
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)


class YOLOPersonDetector:
    """Detects person using YOLOv5 and estimates distance"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.load_model()


    def load_model(self):
        """Load YOLO model using Ultralytics (supports YOLOv8 and YOLOv5u)"""
        try:
            logger.info(f"Loading YOLO model: {self.config.YOLO_MODEL_PATH}")
            
            # Load model from path (can be yolov5s.pt, yolov5su.pt, yolov8n.pt, etc.)
            self.model = YOLO(self.config.YOLO_MODEL_PATH)

            # Optional: Set confidence threshold if available in config
            conf = getattr(self.config, "YOLO_CONFIDENCE", 0.25)
            if hasattr(self.model, "overrides"):
                self.model.overrides["conf"] = conf
            logger.info(f"YOLO model loaded successfully with conf={conf}")

        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise RuntimeError(
                "Failed to load YOLO model. Please ensure:\n"
                "1. ultralytics is installed (pip install ultralytics --upgrade)\n"
                "2. Model path is correct and accessible.\n"
                f"Error detail: {e}"
            )


    def detect_person(self, frame):
        """
        Detect person in a frame using YOLO (Ultralytics format)

        Args:
            frame: BGR image from OpenCV

        Returns:
            tuple: (person_detected, person_bbox, distance_status, confidence)
                person_bbox: (x1, y1, x2, y2) or None
                distance_status: 'far', 'near', 'very_near' or None
        """
        if self.model is None:
            logger.warning("YOLO model not loaded yet.")
            return False, None, None, 0.0

        # Run inference (Ultralytics returns a list of Results)
        results = self.model.predict(frame, verbose=False)

        if not results or len(results[0].boxes) == 0:
            return False, None, None, 0.0

        boxes = results[0].boxes.cpu().numpy()

        # Filter only 'person' class (class id = 0)
        person_detections = [b for b in boxes if int(b.cls[0]) == 0]

        if not person_detections:
            return False, None, None, 0.0

        # Select detection with highest confidence
        best = max(person_detections, key=lambda b: float(b.conf[0]))
        x1, y1, x2, y2 = map(int, best.xyxy[0])
        confidence = float(best.conf[0])
        bbox = (x1, y1, x2, y2)

        # Estimate distance
        distance_status = self._estimate_distance(bbox)

        return True, bbox, distance_status, confidence


    def _estimate_distance(self, bbox):
        """
        Estimate distance based on bounding box height
        
        Args:
            bbox: (x1, y1, x2, y2)
        
        Returns:
            str: 'far' (>5m), 'near' (<5m), 'very_near' (≤0.6m)
        """
        x1, y1, x2, y2 = bbox
        bbox_height = y2 - y1
        
        # Distance thresholds based on bbox height
        # NOTE: These values need calibration based on your camera setup!
        if bbox_height >= self.config.DISTANCE_VERY_NEAR:
            return 'very_near'  # ≤0.6m
        elif bbox_height >= self.config.DISTANCE_NEAR:
            return 'near'  # <5m
        else:
            return 'far'  # >5m
    
    def draw_detection(self, frame, bbox, distance_status, confidence):
        """
        Draw bounding box and info on frame
        
        Args:
            frame: Image to draw on
            bbox: (x1, y1, x2, y2)
            distance_status: 'far', 'near', 'very_near'
            confidence: Detection confidence
        
        Returns:
            frame with drawings
        """
        if bbox is None:
            return frame
        
        x1, y1, x2, y2 = bbox
        
        # Color based on distance
        if distance_status == 'very_near':
            color = (0, 255, 0)  # Green
            text = f"VERY CLOSE ({confidence:.2f})"
        elif distance_status == 'near':
            color = (0, 255, 255)  # Yellow
            text = f"APPROACHING ({confidence:.2f})"
        else:
            color = (0, 165, 255)  # Orange
            text = f"DETECTED ({confidence:.2f})"
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        label_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - 30), (x1 + label_size[0], y1), color, -1)
        
        # Draw label text
        cv2.putText(frame, text, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Draw bbox height (for calibration)
        height_text = f"H: {y2 - y1}px"
        cv2.putText(frame, height_text, (x1, y2 + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame