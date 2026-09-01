import time
import logging
from utils.logger import get_logger

logger = get_logger("hardware")

class ArduinoController:
    """
    Manages serial communication with Arduino hardware controller.
    Provides fallback to Simulation Mode if device is unavailable.
    """
    def __init__(self, port="COM3", baud_rate=9600, simulation_mode=True):
        self.port = port
        self.baud_rate = baud_rate
        self.simulation_mode = simulation_mode
        self.serial_conn = None
        self.is_connected = False
        self.last_command = "NORMAL"
        self.command_log = []

        if not self.simulation_mode:
            self.connect()

    def connect(self):
        """Attempts connection to Arduino serial port."""
        if self.simulation_mode:
            self.is_connected = False
            logger.info("Hardware running in SIMULATION MODE.")
            return False

        try:
            import serial
            self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            self.is_connected = True
            logger.info(f"Arduino successfully connected on {self.port} at {self.baud_rate} baud.")
            return True
        except Exception as e:
            logger.warning(f"Could not connect to Arduino on {self.port}: {e}. Switching to SIMULATION MODE.")
            self.is_connected = False
            self.simulation_mode = True
            return False

    def send_command(self, command):
        """
        Sends a command string ('NORMAL', 'POTHOLE', 'SPEED_BREAKER', 'LOW_SPEED', 'STOP') to Arduino.
        """
        command = command.strip().upper()
        self.last_command = command
        log_entry = f"[{time.strftime('%H:%M:%S')}] COMMAND: {command}"
        self.command_log.append(log_entry)
        if len(self.command_log) > 50:
            self.command_log.pop(0)

        if self.is_connected and self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                logger.info(f"Arduino Hardware Command Sent: {command}")
                return True
            except Exception as e:
                logger.error(f"Failed to send command to Arduino: {e}")
                self.is_connected = False
                return False
        else:
            logger.info(f"[SIMULATED ARDUINO COMMAND]: {command}")
            return True

    def get_status(self):
        """Returns status string and boolean indicator."""
        if self.is_connected:
            return "Connected", "🟢"
        elif self.simulation_mode:
            return "Simulation Mode", "🟡"
        else:
            return "Disconnected", "🔴"

    def close(self):
        """Safely closes serial port."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                logger.info("Arduino serial port closed.")
            except Exception:
                pass
        self.is_connected = False
