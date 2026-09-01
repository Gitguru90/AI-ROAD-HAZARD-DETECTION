# AI Road Hazard Detection & Smart Speed Control System

An advanced computer vision and IoT prototype designed to detect road hazards such as **Potholes** and **Speed Breakers** in real-time, applying temporal frame-buffer smoothing and broadcasting automated speed control alerts to Arduino hardware controllers.

---

## 🚗 Overview

Road hazards like unseen potholes and unmarked speed breakers cause vehicle damage, accidents, and sudden emergency braking. This system leverages deep learning (**Ultralytics YOLO11**) and OpenCV video stream analysis to detect road anomalies ahead of the vehicle. To prevent false positive warnings from single-frame glitches, a temporal sliding window buffer evaluates detection consistency before triggering speed reduction commands.

---

## ✨ Features

- **Multi-Class Detection**: Identifies **Potholes** (Class 0) and **Speed Breakers** (Class 1).
- **Temporal Frame-Buffer Smoothing**: Utilizes a `deque` sliding window to confirm hazard presence across consecutive frames.
- **Hardware Controller Integration**: Sends PySerial commands (`NORMAL`, `POTHOLE`, `SPEED_BREAKER`, `LOW_SPEED`) to Arduino LED/Buzzer systems.
- **Hardware Simulation Mode**: Runs seamlessly without physical Arduino hardware connected.
- **Interactive Streamlit Dashboard**: Includes real-time status banners, live FPS counters, hazard cards, and configurable parameters.
- **Analytics & History Logging**: Logs confirmed events to CSV with Plotly data visualization charts.
- **Dataset Pipeline Tools**: Includes helper scripts for relabeling speed breaker datasets, merging collections, and verifying bounding box coordinates.

---

## 🏗 System Architecture

```
USER / VEHICLE CAMERA
       │
       ▼
   Streamlit Dashboard
       │
       ├── Upload Video / Live Camera Stream / Demo Mode
       │
       ▼
  OpenCV Frame Extraction
       │
       ▼
 Ultralytics YOLO11 Model (Inference)
       │
       ▼
  Confidence Threshold Filter
       │
       ▼
 Temporal Frame Buffer Smoothing (deque)
       │
       ▼
  Hazard State Machine (NORMAL / POTHOLE / SPEED_BREAKER)
       │
       ├──► Update Dashboard UI Status Panel (RED / AMBER / GREEN)
       │
       ├──► Transmit PySerial Signal to Arduino Controller
       │
       ├──► Record Event to History CSV
       │
       └──► Render Plotly Analytics Charts
```

---

## 💻 Technology Stack

- **Language**: Python 3.x
- **Computer Vision**: OpenCV, Ultralytics YOLO11, PyTorch
- **Frontend / Dashboard**: Streamlit
- **Visualization**: Plotly, Pandas
- **Hardware**: Arduino (C++), PySerial
- **Logging**: Python Logging

---

## 📂 Project Structure

```
AI-ROAD-HAZARD-DETECTION/
│
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore definitions
│
├── models/
│   └── my_model.pt             # Trained YOLO11 model weights
│
├── config/
│   └── config.py               # Path definitions & settings manager
│
├── modules/
│   ├── detector.py             # YOLO11 inference wrapper & demo fallback
│   ├── video_processor.py      # OpenCV video frame drawer & overlays
│   ├── hazard_logic.py         # Frame-buffer temporal smoothing logic
│   ├── hardware.py             # PySerial Arduino manager & simulation
│   ├── history.py              # CSV history persistence
│   └── analytics.py            # Plotly interactive chart builders
│
├── ui/
│   ├── dashboard.py            # Multi-page layout controller
│   ├── components.py           # Status cards & UI widgets
│   └── styles.py               # Custom glassmorphism dark CSS
│
├── data/
│   ├── detection_history.csv   # Event log file
│   └── settings.json           # Saved user preferences
│
├── training/
│   ├── Train_YOLO_Models.ipynb # Training notebook
│   ├── classes.txt             # Class labels file
│   └── data.yaml               # YOLO dataset configuration
│
├── arduino/
│   └── road_hazard_controller.ino # Arduino C++ sketch
│
├── videos/
│   └── sample.mp4              # Sample video directory
│
└── utils/
    ├── logger.py               # Application logging setup
    ├── helpers.py              # Timestamp & formatting helpers
    ├── relabel_speed_breaker.py# Class index converter (0 -> 1)
    ├── merge_dataset.py        # Safe dataset merger
    └── validate_dataset.py     # YOLO dataset integrity checker
```

---

## ⚙️ Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd AI-ROAD-HAZARD-DETECTION
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🔌 Arduino Hardware Setup

### Hardware Circuit Components
- Arduino Uno / Nano
- Green LED (Normal Clear Road) -> Pin 8
- Red LED (Pothole Alert) -> Pin 9
- Yellow LED (Speed Breaker Alert) -> Pin 10
- Buzzer (Audio Alert) -> Pin 11

### Uploading Sketch
1. Open `arduino/road_hazard_controller.ino` in the Arduino IDE.
2. Select your board and COM port.
3. Upload the sketch.
4. Set the COM port in the dashboard **Settings** page (e.g., `COM3`, baud `9600`).

---

## 🟡 Simulation Mode

If an Arduino is not connected or the model weights `models/my_model.pt` are missing:
- The system automatically enters **Simulation Mode**.
- Synthetic hazard video frames demonstrate detection behaviors.
- Simulated Arduino serial commands (`NORMAL`, `POTHOLE`, `SPEED_BREAKER`, `LOW_SPEED`) display on the UI without throwing crashes.

---

## 📊 Dataset Preparation & Relabeling

1. **Relabel Speed Breaker dataset (if class 0 originally)**:
   ```bash
   python utils/relabel_speed_breaker.py --labels-dir path/to/speed_breaker/labels
   ```
2. **Merge Pothole and Speed Breaker datasets**:
   ```bash
   python utils/merge_dataset.py --pothole-dir path/to/pothole --sb-dir path/to/sb --output-dir dataset_merged
   ```
3. **Validate Dataset Health**:
   ```bash
   python utils/validate_dataset.py --dataset-dir dataset_merged
   ```

---

## 💡 Future Roadmap

- GPS Coordinate Tagging & Google Maps Hazard Pinning.
- Distance-based braking urgency estimation.
- Cloud DB Sync & Automatic Road Quality Report Generation.

---

## ⚠️ Disclaimer

This system is an AI/IoT research prototype intended for academic demonstrations, hackathons, and driver assistance evaluation. It should not be used as a primary vehicle control device without automotive-grade validation.
