import os
import time
import threading
from datetime import datetime

def format_timestamp():
    """Returns current timestamp formatted for history logging."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_frame_time(frame_idx, fps):
    """Calculates time formatted as MM:SS from frame index and FPS."""
    if not fps or fps <= 0:
        return "00:00"
    seconds = int(frame_idx / fps)
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def play_voice_alert_async(message):
    """
    Optional voice alert utility. Runs in a non-blocking daemon thread.
    Uses pyttsx3 if available, or win32com.client on Windows as fallback.
    """
    def _speak():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(message)
            engine.runAndWait()
        except Exception:
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(message)
            except Exception:
                pass

    t = threading.Thread(target=_speak, daemon=True)
    t.start()
