import os
import pandas as pd
from pathlib import Path
from config.config import HISTORY_FILE, DATA_DIR
from utils.logger import get_logger

logger = get_logger("history")

COLUMNS = ["Timestamp", "Hazard", "Confidence", "Frame", "Video", "Arduino Action"]

def init_history():
    """Ensures CSV history file exists with proper headers."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(HISTORY_FILE, index=False)

def add_record(timestamp, hazard, confidence, frame_num, video_name="live_stream", arduino_action="LOW_SPEED"):
    """
    Appends a new hazard detection event record to CSV history.
    """
    init_history()
    try:
        conf_str = f"{int(confidence * 100)}%" if isinstance(confidence, float) else str(confidence)
        frame_str = f"Frame {frame_num}"
        
        new_row = {
            "Timestamp": timestamp,
            "Hazard": hazard,
            "Confidence": conf_str,
            "Frame": frame_str,
            "Video": video_name,
            "Arduino Action": arduino_action
        }
        
        df = pd.DataFrame([new_row])
        df.to_csv(HISTORY_FILE, mode='a', header=False, index=False)
        logger.info(f"Recorded history entry: {hazard} at {frame_str}")
        return True
    except Exception as e:
        logger.error(f"Failed to record detection history: {e}")
        return False

def load_history():
    """Loads detection history as pandas DataFrame."""
    init_history()
    try:
        df = pd.read_csv(HISTORY_FILE)
        return df
    except Exception as e:
        logger.error(f"Error loading history CSV: {e}")
        return pd.DataFrame(columns=COLUMNS)

def clear_history():
    """Clears all records in history CSV."""
    init_history()
    try:
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(HISTORY_FILE, index=False)
        logger.info("Detection history cleared.")
        return True
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return False

def export_csv():
    """Returns CSV string data for download."""
    df = load_history()
    return df.to_csv(index=False).encode('utf-8')
