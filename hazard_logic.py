from collections import deque
import time
from utils.logger import get_logger

logger = get_logger("hazard_logic")

class HazardLogicProcessor:
    """
    Temporal frame-buffer smoothing and hazard state decision engine.
    Prevents single-frame false triggers and flickering warnings.
    """
    def __init__(self, buffer_size=10, detection_ratio=0.50):
        self.buffer_size = buffer_size
        self.detection_ratio = detection_ratio
        self.frame_buffer = deque(maxlen=buffer_size)
        self.conf_buffer = deque(maxlen=buffer_size)
        
        # State tracking
        self.current_status = "NORMAL"         # NORMAL, POTHOLE, SPEED_BREAKER
        self.recommended_action = "NORMAL SPEED" # NORMAL SPEED, REDUCE SPEED
        self.last_confirmed_hazard = None
        self.active_confidence = 0.0
        self.total_processed_frames = 0
        self.pothole_count = 0
        self.speed_breaker_count = 0
        self.last_state_change_time = time.time()

    def update_settings(self, buffer_size, detection_ratio):
        """Updates smoothing buffer parameters dynamically."""
        if buffer_size != self.buffer_size:
            self.buffer_size = buffer_size
            # Re-create deque keeping latest elements
            items = list(self.frame_buffer)
            self.frame_buffer = deque(items, maxlen=buffer_size)
            self.conf_buffer = deque(list(self.conf_buffer), maxlen=buffer_size)
        self.detection_ratio = detection_ratio

    def process_frame_detections(self, detections):
        """
        Processes detections for the current frame and updates system state.
        
        Returns a dict:
        {
            "status": "NORMAL" | "POTHOLE" | "SPEED_BREAKER",
            "action": "NORMAL SPEED" | "REDUCE SPEED",
            "arduino_cmd": "NORMAL" | "POTHOLE" | "SPEED_BREAKER" | "LOW_SPEED",
            "confidence": float,
            "confirmed": bool,
            "frame_hazard": str,
            "hazard_display": str
        }
        """
        self.total_processed_frames += 1
        
        # Find dominant hazard in frame
        frame_hazard = "clear"
        frame_max_conf = 0.0
        
        if detections:
            # Sort by confidence descending
            sorted_dets = sorted(detections, key=lambda x: x["confidence"], reverse=True)
            top_det = sorted_dets[0]
            frame_hazard = top_det["class_name"]
            frame_max_conf = top_det["confidence"]

        # Append to temporal buffers
        self.frame_buffer.append(frame_hazard)
        self.conf_buffer.append(frame_max_conf if frame_hazard != "clear" else 0.0)

        # Count occurrences in buffer
        pothole_ratio = self.frame_buffer.count("pothole") / len(self.frame_buffer)
        sb_ratio = self.frame_buffer.count("speed_breaker") / len(self.frame_buffer)

        # Confirm hazard if ratio threshold met
        confirmed_status = "NORMAL"
        rec_action = "NORMAL SPEED"
        arduino_cmd = "NORMAL"
        active_conf = 0.0
        confirmed = False
        hazard_display = "🟢 ROAD CLEAR"

        if pothole_ratio >= self.detection_ratio and pothole_ratio >= sb_ratio:
            confirmed_status = "POTHOLE"
            rec_action = "REDUCE SPEED"
            arduino_cmd = "POTHOLE"
            pothole_confs = [c for h, c in zip(self.frame_buffer, self.conf_buffer) if h == "pothole"]
            active_conf = sum(pothole_confs) / len(pothole_confs) if pothole_confs else frame_max_conf
            confirmed = True
            hazard_display = "🕳️ POTHOLE DETECTED"
            if self.current_status != "POTHOLE":
                self.pothole_count += 1

        elif sb_ratio >= self.detection_ratio:
            confirmed_status = "SPEED_BREAKER"
            rec_action = "REDUCE SPEED"
            arduino_cmd = "SPEED_BREAKER"
            sb_confs = [c for h, c in zip(self.frame_buffer, self.conf_buffer) if h == "speed_breaker"]
            active_conf = sum(sb_confs) / len(sb_confs) if sb_confs else frame_max_conf
            confirmed = True
            hazard_display = "🚧 SPEED BREAKER DETECTED"
            if self.current_status != "SPEED_BREAKER":
                self.speed_breaker_count += 1

        self.current_status = confirmed_status
        self.recommended_action = rec_action
        self.active_confidence = active_conf

        return {
            "status": confirmed_status,
            "action": rec_action,
            "arduino_cmd": arduino_cmd,
            "confidence": active_conf,
            "confirmed": confirmed,
            "frame_hazard": frame_hazard,
            "hazard_display": hazard_display,
            "pothole_ratio": pothole_ratio,
            "sb_ratio": sb_ratio
        }

    def reset(self):
        """Resets frame buffer and counters for new video session."""
        self.frame_buffer.clear()
        self.conf_buffer.clear()
        self.current_status = "NORMAL"
        self.recommended_action = "NORMAL SPEED"
        self.active_confidence = 0.0
        self.total_processed_frames = 0
        self.pothole_count = 0
        self.speed_breaker_count = 0
