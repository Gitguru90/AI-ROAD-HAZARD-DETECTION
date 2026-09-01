import os
import json
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
MODULES_DIR = BASE_DIR / "modules"
UI_DIR = BASE_DIR / "ui"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
VIDEOS_DIR = BASE_DIR / "videos"
TRAINING_DIR = BASE_DIR / "training"
ARDUINO_DIR = BASE_DIR / "arduino"
UTILS_DIR = BASE_DIR / "utils"

# Default Model File
DEFAULT_MODEL_PATH = MODELS_DIR / "my_model.pt"

# Files
HISTORY_FILE = DATA_DIR / "detection_history.csv"
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE = LOGS_DIR / "app.log"
SAMPLE_VIDEO_PATH = VIDEOS_DIR / "sample.mp4"

# Default System Configuration
DEFAULT_SETTINGS = {
    "model_path": str(DEFAULT_MODEL_PATH),
    "confidence_threshold": 0.50,
    "buffer_size": 10,
    "detection_ratio": 0.50,
    "camera_id": 0,
    "serial_port": "COM3",
    "baud_rate": 9600,
    "simulation_mode": True,
    "voice_alerts": False
}

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        MODELS_DIR, DATA_DIR, LOGS_DIR, VIDEOS_DIR,
        TRAINING_DIR, ARDUINO_DIR, UTILS_DIR
    ]
    for d in directories:
        d.mkdir(parents=True, exist_ok=True)

def load_settings():
    """Load settings from settings.json or return default settings."""
    ensure_directories()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                # Fill missing keys with defaults
                for key, val in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = val
                return settings
        except Exception:
            return DEFAULT_SETTINGS.copy()
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

def save_settings(settings_dict):
    """Save settings dictionary to settings.json."""
    ensure_directories()
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings_dict, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
