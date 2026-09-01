import cv2
import time
import numpy as np
from utils.logger import get_logger

logger = get_logger("video_processor")

# Color palette (BGR for OpenCV)
COLOR_POTHOLE = (40, 40, 230)       # Crimson / Red
COLOR_SPEED_BREAKER = (0, 165, 255) # Amber / Orange-Yellow
COLOR_CLEAR = (80, 200, 120)        # Emerald Green
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (15, 23, 42)

def annotate_frame(frame, detections, hazard_state):
    """
    Overlays bounding boxes, labels, confidence scores, and status banner onto an OpenCV frame.
    
    hazard_state format:
    {
        "status": "NORMAL" | "POTHOLE" | "SPEED_BREAKER",
        "action": "NORMAL SPEED" | "REDUCE SPEED",
        "confidence": float,
        "hazard_display": str
    }
    """
    annotated = frame.copy()
    h, w = annotated.shape[:2]

    # 1. Draw Bounding Boxes for Detections
    for det in detections:
        bbox = det["bbox"]
        cls_name = det["class_name"]
        conf = det["confidence"]

        x1, y1, x2, y2 = bbox

        if cls_name.lower() == "pothole":
            color = COLOR_POTHOLE
            label_text = f"POTHOLE {int(conf * 100)}%"
        else:
            color = COLOR_SPEED_BREAKER
            label_text = f"SPEED BREAKER {int(conf * 100)}%"

        # Draw main rectangle
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)

        # Draw label header box
        (font_w, font_h), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(annotated, (x1, y1 - font_h - 10), (x1 + font_w + 10, y1), color, -1)
        cv2.putText(annotated, label_text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2, cv2.LINE_AA)

    # 2. Draw Top Status Banner
    status = hazard_state.get("status", "NORMAL")
    if status == "POTHOLE":
        banner_color = COLOR_POTHOLE
        banner_text = "ALERT: POTHOLE DETECTED - REDUCE SPEED"
    elif status == "SPEED_BREAKER":
        banner_color = COLOR_SPEED_BREAKER
        banner_text = "ALERT: SPEED BREAKER DETECTED - REDUCE SPEED"
    else:
        banner_color = COLOR_CLEAR
        banner_text = "ROAD CLEAR - NORMAL SPEED"

    # Semi-transparent top bar overlay
    overlay = annotated.copy()
    cv2.rectangle(overlay, (0, 0), (w, 45), banner_color, -1)
    cv2.addWeighted(overlay, 0.85, annotated, 0.15, 0, annotated)

    # Draw Banner Text
    cv2.putText(annotated, banner_text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, COLOR_WHITE, 2, cv2.LINE_AA)

    return annotated

def generate_synthetic_demo_frame(frame_idx):
    """
    Generates a realistic synthetic road frame with moving line perspectives
    and simulated potholes/speed breakers when no video file is provided.
    """
    w, h = 640, 360
    # Dark asphalt background
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = (45, 42, 40)

    # Road lanes perspective
    vp_x, vp_y = w // 2, int(h * 0.3)
    cv2.line(frame, (vp_x, vp_y), (50, h), (180, 180, 180), 2)
    cv2.line(frame, (vp_x, vp_y), (w - 50, h), (180, 180, 180), 2)

    # Center dash lines (animated)
    dash_offset = (frame_idx * 15) % 80
    for y in range(vp_y, h, 40):
        curr_y = y + dash_offset
        if curr_y < h:
            # Perspective scale
            scale = (curr_y - vp_y) / (h - vp_y)
            line_w = max(2, int(10 * scale))
            cv2.line(frame, (vp_x, curr_y), (vp_x, min(h, curr_y + 15)), (255, 255, 255), line_w)

    # Simulated hazard graphics
    t_sec = (frame_idx // 15) % 10
    if t_sec in [2, 3, 4]:
        # Draw dark pothole oval
        cv2.ellipse(frame, (w // 2 - 20, int(h * 0.65)), (40, 20), 0, 0, 360, (20, 20, 20), -1)
        cv2.ellipse(frame, (w // 2 - 20, int(h * 0.65)), (42, 22), 0, 0, 360, (70, 70, 70), 2)
    elif t_sec in [7, 8]:
        # Draw yellow speed breaker stripes
        sb_y = int(h * 0.7)
        cv2.rectangle(frame, (120, sb_y), (w - 120, sb_y + 25), (0, 180, 240), -1)
        for x in range(120, w - 120, 40):
            cv2.rectangle(frame, (x, sb_y), (x + 20, sb_y + 25), (20, 20, 20), -1)

    return frame
