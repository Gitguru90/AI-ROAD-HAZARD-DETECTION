import os
import time
import random
import cv2
import numpy as np
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("detector")

class HazardDetector:
    """
    YOLO11 Object Detector for Road Hazards (Potholes and Speed Breakers).
    """
    def __init__(self, model_path="models/my_model.pt", conf_threshold=0.50):
        self.model_path = Path(model_path)
        self.conf_threshold = conf_threshold
        self.model = None
        self.is_loaded = False
        self.class_names = {0: "pothole", 1: "speed_breaker"}
        self.load_error = None
        self.load_model()

    def load_model(self):
        """Loads Ultralytics YOLO model from specified weights path."""
        if not self.model_path.exists():
            self.is_loaded = False
            self.load_error = f"Model file not found at '{self.model_path}'. Using DEMO Mode."
            logger.warning(self.load_error)
            return False

        try:
            from ultralytics import YOLO
            self.model = YOLO(str(self.model_path))
            self.is_loaded = True
            
            # Read class names dynamically from model
            if hasattr(self.model, "names") and self.model.names:
                self.class_names = self.model.names
            logger.info(f"YOLO model successfully loaded from {self.model_path}. Classes: {self.class_names}")
            return True
        except Exception as e:
            self.is_loaded = False
            self.load_error = f"Failed to load model: {str(e)}"
            logger.error(self.load_error)
            return False

    def predict(self, frame, conf_threshold=None):
        """
        Runs object detection on a single OpenCV frame (BGR numpy array).
        Returns list of detection dictionaries:
        [
            {
                "class_id": int,
                "class_name": str,
                "confidence": float,
                "bbox": [x1, y1, x2, y2]
            }, ...
        ]
        """
        threshold = conf_threshold if conf_threshold is not None else self.conf_threshold
        detections = []

        if not self.is_loaded or self.model is None:
            # Return demo/simulated detections if model is not loaded
            return self._generate_demo_detections(frame, threshold)

        try:
            results = self.model(frame, conf=threshold, verbose=False)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].cpu().numpy().astype(int).tolist()
                    
                    cls_name = self.class_names.get(cls_id, f"class_{cls_id}")
                    
                    # Normalize naming convention
                    if "pothole" in cls_name.lower():
                        cls_name = "pothole"
                    elif "speed" in cls_name.lower() or "breaker" in cls_name.lower() or "bump" in cls_name.lower():
                        cls_name = "speed_breaker"

                    detections.append({
                        "class_id": cls_id,
                        "class_name": cls_name,
                        "confidence": conf,
                        "bbox": xyxy
                    })
        except Exception as e:
            logger.error(f"Error during YOLO inference: {e}")

        return detections

    def _generate_demo_detections(self, frame, threshold):
        """Generates predictable synthetic detections for UI testing/Demo mode."""
        h, w = frame.shape[:2]
        detections = []
        
        # Deterministic pseudo-randomness based on frame average color / time
        t_sec = int(time.time() * 2) % 10
        if t_sec in [2, 3, 4]:
            # Pothole simulated box
            detections.append({
                "class_id": 0,
                "class_name": "pothole",
                "confidence": 0.89 + random.uniform(-0.03, 0.05),
                "bbox": [int(w*0.3), int(h*0.6), int(w*0.5), int(h*0.75)]
            })
        elif t_sec in [7, 8]:
            # Speed breaker simulated box
            detections.append({
                "class_id": 1,
                "class_name": "speed_breaker",
                "confidence": 0.92 + random.uniform(-0.02, 0.04),
                "bbox": [int(w*0.2), int(h*0.7), int(w*0.8), int(h*0.82)]
            })
        
        return [d for d in detections if d["confidence"] >= threshold]
