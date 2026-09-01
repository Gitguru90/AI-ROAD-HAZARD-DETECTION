import time
import tempfile
import cv2
import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

from config.config import load_settings, save_settings, DEFAULT_MODEL_PATH
from ui.styles import apply_custom_styles
from ui.components import (
    render_header,
    render_sidebar_status,
    render_stat_card,
    render_status_panel,
    render_hazard_detail_card
)
from modules.detector import HazardDetector
from modules.hazard_logic import HazardLogicProcessor
from modules.hardware import ArduinoController
from modules.video_processor import annotate_frame, generate_synthetic_demo_frame
from modules.history import load_history, add_record, clear_history, export_csv
from modules.analytics import (
    get_analytics_summary,
    create_hazard_pie_chart,
    create_confidence_histogram,
    create_timeline_chart,
    create_video_source_chart
)
from utils.helpers import format_timestamp, format_frame_time, play_voice_alert_async

def init_session_state():
    """Initializes Streamlit session state variables."""
    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()
    
    if "detector" not in st.session_state:
        st.session_state.detector = HazardDetector(
            model_path=st.session_state.settings["model_path"],
            conf_threshold=st.session_state.settings["confidence_threshold"]
        )

    if "logic" not in st.session_state:
        st.session_state.logic = HazardLogicProcessor(
            buffer_size=st.session_state.settings["buffer_size"],
            detection_ratio=st.session_state.settings["detection_ratio"]
        )

    if "arduino" not in st.session_state:
        st.session_state.arduino = ArduinoController(
            port=st.session_state.settings["serial_port"],
            baud_rate=st.session_state.settings["baud_rate"],
            simulation_mode=st.session_state.settings["simulation_mode"]
        )

    if "detection_active" not in st.session_state:
        st.session_state.detection_active = False

def render_app():
    """Main rendering entry point."""
    apply_custom_styles()
    init_session_state()

    # Sidebar Navigation
    st.sidebar.image("https://img.icons8.com/isometric/100/car.png", width=64)
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Detection", "History", "Analytics", "Settings", "About"],
        index=0
    )

    # Render Sidebar System Status
    render_sidebar_status(
        model_loaded=st.session_state.detector.is_loaded,
        hardware_status=st.session_state.arduino.get_status(),
        camera_available=True
    )

    # Page Routing
    if page == "Dashboard":
        render_dashboard_page()
    elif page == "Detection":
        render_detection_page()
    elif page == "History":
        render_history_page()
    elif page == "Analytics":
        render_analytics_page()
    elif page == "Settings":
        render_settings_page()
    elif page == "About":
        render_about_page()

def render_dashboard_page():
    """Renders the primary Dashboard home view."""
    render_header()
    
    # 4 Main Overview Cards
    df_hist = load_history()
    summary = get_analytics_summary(df_hist)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_stat_card("Total Hazards", summary["total_hazards"], "🚨"), unsafe_allow_html=True)
    with c2:
        st.markdown(render_stat_card("Potholes", summary["potholes"], "🕳️"), unsafe_allow_html=True)
    with c3:
        st.markdown(render_stat_card("Speed Breakers", summary["speed_breakers"], "🚧"), unsafe_allow_html=True)
    with c4:
        st.markdown(render_stat_card("Current Status", "NORMAL SPEED", "🟢"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # System Status & Quick Launch
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("📌 System Highlights")
        st.info("""
        **Welcome to the AI Road Hazard Detection & Smart Speed Control System.**
        - Uses Ultralytics **YOLO11** object detection for real-time hazard identification.
        - Applies **temporal frame-buffer smoothing** to prevent false triggers.
        - Sends real-time speed reduction signals to **Arduino hardware** or **Simulation Mode**.
        """)
        
        st.markdown("#### Model & Hardware Config")
        st.write(f"- **Active Model**: `{st.session_state.settings['model_path']}` ({'Loaded 🟢' if st.session_state.detector.is_loaded else 'Missing/Demo 🔴'})")
        st.write(f"- **Serial Port**: `{st.session_state.settings['serial_port']}` @ `{st.session_state.settings['baud_rate']}`")
        st.write(f"- **Confidence Threshold**: `{st.session_state.settings['confidence_threshold']}`")
        st.write(f"- **Buffer Smoothing**: `{st.session_state.settings['buffer_size']} frames` @ `{int(st.session_state.settings['detection_ratio']*100)}% ratio`")

    with col_right:
        st.subheader("🎯 Quick Action")
        st.write("Launch hazard detection pipeline on sample video or live feed.")
        if st.button("🚀 GO TO DETECTION PAGE", use_container_width=True):
            st.session_state.page = "Detection"
            st.rerun()

def render_detection_page():
    """Renders the main video upload, live camera, and demo detection page."""
    render_header()
    st.subheader("📹 Hazard Detection Workspace")

    mode = st.radio(
        "Select Detection Input Mode",
        ["Upload Video", "Live Camera", "Demo Mode"],
        horizontal=True
    )

    if not st.session_state.detector.is_loaded:
        st.warning("⚠️ Trained model file `models/my_model.pt` not found. System is running in DEMO / SIMULATION MODE with synthetic hazard generation.")

    col_video, col_status = st.columns([2.2, 1.2])

    video_placeholder = col_video.empty()
    status_placeholder = col_status.empty()
    hazard_info_placeholder = st.empty()
    stats_placeholder = st.empty()

    # Initial status display
    with status_placeholder:
        render_status_panel({"status": "NORMAL", "confidence": 0.0})

    if mode == "Upload Video":
        uploaded_file = st.file_uploader("Upload Road Video (MP4, AVI, MOV, MKV)", type=["mp4", "avi", "mov", "mkv"])
        
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            tfile.write(uploaded_file.read())
            video_path = tfile.name

            col_btn1, col_btn2 = st.columns(2)
            start_btn = col_btn1.button("▶️ START DETECTION", use_container_width=True)
            stop_btn = col_btn2.button("⏹️ STOP DETECTION", use_container_width=True)

            if start_btn:
                st.session_state.detection_active = True
                _run_video_detection_loop(
                    source=video_path,
                    source_name=uploaded_file.name,
                    video_placeholder=video_placeholder,
                    status_placeholder=status_placeholder,
                    hazard_info_placeholder=hazard_info_placeholder,
                    stats_placeholder=stats_placeholder
                )

    elif mode == "Live Camera":
        cam_id = st.session_state.settings["camera_id"]
        st.info(f"Connected Camera Device ID: `{cam_id}`")
        
        col_btn1, col_btn2 = st.columns(2)
        start_btn = col_btn1.button("📷 START CAMERA", use_container_width=True)
        stop_btn = col_btn2.button("⏹️ STOP CAMERA", use_container_width=True)

        if start_btn:
            st.session_state.detection_active = True
            _run_video_detection_loop(
                source=cam_id,
                source_name="Live Camera",
                video_placeholder=video_placeholder,
                status_placeholder=status_placeholder,
                hazard_info_placeholder=hazard_info_placeholder,
                stats_placeholder=stats_placeholder
            )

    elif mode == "Demo Mode":
        st.info("Demonstration mode runs synthetic video frames with simulated pothole and speed breaker triggers.")
        col_btn1, col_btn2 = st.columns(2)
        start_btn = col_btn1.button("🎬 RUN DEMO SIMULATION", use_container_width=True)
        stop_btn = col_btn2.button("⏹️ STOP DEMO", use_container_width=True)

        if start_btn:
            st.session_state.detection_active = True
            _run_demo_simulation_loop(
                video_placeholder=video_placeholder,
                status_placeholder=status_placeholder,
                hazard_info_placeholder=hazard_info_placeholder,
                stats_placeholder=stats_placeholder
            )

def _run_video_detection_loop(source, source_name, video_placeholder, status_placeholder, hazard_info_placeholder, stats_placeholder):
    """Executes frame-by-frame YOLO detection on OpenCV video capture."""
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        st.error(f"Error: Unable to open video source '{source}'. Please check file or camera connection.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    st.session_state.logic.reset()

    frame_idx = 0
    pothole_count = 0
    sb_count = 0
    conf_list = []
    start_time = time.time()
    last_arduino_cmd = ""
    last_logged_hazard = None

    while cap.isOpened() and st.session_state.detection_active:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1
        
        # YOLO Detection
        conf_thresh = st.session_state.settings["confidence_threshold"]
        detections = st.session_state.detector.predict(frame, conf_threshold=conf_thresh)

        # Hazard Logic Temporal Buffer
        hazard_state = st.session_state.logic.process_frame_detections(detections)
        status = hazard_state["status"]
        arduino_cmd = hazard_state["arduino_cmd"]
        conf = hazard_state["confidence"]

        if conf > 0:
            conf_list.append(conf)

        # Annotate OpenCV Frame
        annotated_frame = annotate_frame(frame, detections, hazard_state)
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        # Render Right Panel Status
        with status_placeholder:
            render_status_panel(hazard_state)

        # Arduino Hardware Signal Transmission
        if arduino_cmd != last_arduino_cmd:
            st.session_state.arduino.send_command(arduino_cmd)
            last_arduino_cmd = arduino_cmd

            # Voice alert if enabled
            if st.session_state.settings.get("voice_alerts") and status != "NORMAL":
                play_voice_alert_async(f"{status.replace('_', ' ')} detected. Please reduce speed.")

        # Log confirmed detection to History
        if hazard_state["confirmed"] and status != last_logged_hazard:
            timestamp = format_timestamp()
            add_record(
                timestamp=timestamp,
                hazard=status.replace("_", " ").title(),
                confidence=conf,
                frame_num=frame_idx,
                video_name=source_name,
                arduino_action=arduino_cmd
            )
            last_logged_hazard = status
            if status == "POTHOLE":
                pothole_count += 1
            elif status == "SPEED_BREAKER":
                sb_count += 1
        elif not hazard_state["confirmed"]:
            last_logged_hazard = None

        # Time formatting
        time_str = format_frame_time(frame_idx, fps)
        
        with hazard_info_placeholder:
            render_hazard_detail_card(hazard_state, frame_idx=frame_idx, time_str=time_str)

        # Live Performance Stats
        elapsed = max(0.001, time.time() - start_time)
        curr_fps = frame_idx / elapsed
        avg_conf_val = f"{int((sum(conf_list)/len(conf_list))*100)}%" if conf_list else "0%"

        with stats_placeholder:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Frames Processed", frame_idx)
            m2.metric("FPS", f"{curr_fps:.1f}")
            m3.metric("Potholes", pothole_count)
            m4.metric("Speed Breakers", sb_count)
            m5.metric("Avg Confidence", avg_conf_val)

        time.sleep(0.01)

    cap.release()
    st.session_state.detection_active = False
    st.success("Detection completed or stopped.")

def _run_demo_simulation_loop(video_placeholder, status_placeholder, hazard_info_placeholder, stats_placeholder):
    """Executes synthetic frame generation for demonstration mode."""
    st.session_state.logic.reset()
    frame_idx = 0
    pothole_count = 0
    sb_count = 0
    conf_list = []
    start_time = time.time()
    last_arduino_cmd = ""
    last_logged_hazard = None

    for _ in range(300): # 300 synthetic frames
        if not st.session_state.detection_active:
            break
            
        frame_idx += 1
        frame = generate_synthetic_demo_frame(frame_idx)
        
        conf_thresh = st.session_state.settings["confidence_threshold"]
        detections = st.session_state.detector.predict(frame, conf_threshold=conf_thresh)
        hazard_state = st.session_state.logic.process_frame_detections(detections)
        
        status = hazard_state["status"]
        arduino_cmd = hazard_state["arduino_cmd"]
        conf = hazard_state["confidence"]

        if conf > 0:
            conf_list.append(conf)

        annotated_frame = annotate_frame(frame, detections, hazard_state)
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        with status_placeholder:
            render_status_panel(hazard_state)

        if arduino_cmd != last_arduino_cmd:
            st.session_state.arduino.send_command(arduino_cmd)
            last_arduino_cmd = arduino_cmd

        if hazard_state["confirmed"] and status != last_logged_hazard:
            timestamp = format_timestamp()
            add_record(
                timestamp=timestamp,
                hazard=status.replace("_", " ").title(),
                confidence=conf,
                frame_num=frame_idx,
                video_name="Demo_Simulation.mp4",
                arduino_action=arduino_cmd
            )
            last_logged_hazard = status
            if status == "POTHOLE": pothole_count += 1
            elif status == "SPEED_BREAKER": sb_count += 1
        elif not hazard_state["confirmed"]:
            last_logged_hazard = None

        time_str = format_frame_time(frame_idx, 25.0)
        with hazard_info_placeholder:
            render_hazard_detail_card(hazard_state, frame_idx=frame_idx, time_str=time_str)

        elapsed = max(0.001, time.time() - start_time)
        curr_fps = frame_idx / elapsed
        avg_conf_val = f"{int((sum(conf_list)/len(conf_list))*100)}%" if conf_list else "0%"

        with stats_placeholder:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Frames Processed", frame_idx)
            m2.metric("FPS", f"{curr_fps:.1f}")
            m3.metric("Potholes", pothole_count)
            m4.metric("Speed Breakers", sb_count)
            m5.metric("Avg Confidence", avg_conf_val)

        time.sleep(0.03)

    st.session_state.detection_active = False

def render_history_page():
    """Renders detection history table and CSV export."""
    render_header()
    st.subheader("📋 Detection History Log")
    
    df = load_history()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"Total Recorded Detections: `{len(df)}`")
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            clear_history()
            st.success("History log cleared!")
            st.rerun()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        csv_data = export_csv()
        st.download_button(
            label="📥 Export History as CSV",
            data=csv_data,
            file_name="detection_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No detection history recorded yet. Run a detection session to capture events.")

def render_analytics_page():
    """Renders interactive Plotly charts."""
    render_header()
    st.subheader("📊 Hazard Detection Analytics")

    df = load_history()
    summary = get_analytics_summary(df)

    # Top metric indicators
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Hazards Detected", summary["total_hazards"])
    c2.metric("Total Potholes", summary["potholes"])
    c3.metric("Total Speed Breakers", summary["speed_breakers"])
    c4.metric("Average Confidence", summary["avg_confidence"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Visual Charts
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(create_hazard_pie_chart(df), use_container_width=True)
    with g2:
        st.plotly_chart(create_confidence_histogram(df), use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        st.plotly_chart(create_timeline_chart(df), use_container_width=True)
    with g4:
        st.plotly_chart(create_video_source_chart(df), use_container_width=True)

def render_settings_page():
    """Renders system configuration settings page."""
    render_header()
    st.subheader("⚙️ System Configuration")

    with st.form("settings_form"):
        st.markdown("#### 1. AI Model Parameters")
        model_path = st.text_input("YOLO Model Weights Path", value=st.session_state.settings["model_path"])
        conf_thresh = st.slider("Confidence Threshold", min_value=0.10, max_value=0.95, value=float(st.session_state.settings["confidence_threshold"]), step=0.05)

        st.markdown("#### 2. Temporal Smoothing & Frame Buffer")
        buffer_size = st.slider("Frame Buffer Size", min_value=1, max_value=30, value=int(st.session_state.settings["buffer_size"]), step=1)
        det_ratio = st.slider("Detection Ratio Threshold", min_value=0.10, max_value=1.00, value=float(st.session_state.settings["detection_ratio"]), step=0.05)

        st.markdown("#### 3. Hardware & Serial Port")
        camera_id = st.number_input("Camera Index ID", min_value=0, max_value=5, value=int(st.session_state.settings["camera_id"]))
        serial_port = st.text_input("Arduino Serial Port", value=st.session_state.settings["serial_port"])
        baud_rate = st.selectbox("Baud Rate", [9600, 19200, 38400, 57600, 115200], index=0)

        st.markdown("#### 4. System Toggles")
        sim_mode = st.checkbox("Enable Hardware Simulation Mode", value=bool(st.session_state.settings["simulation_mode"]))
        voice_alerts = st.checkbox("Enable Voice Alerts", value=bool(st.session_state.settings["voice_alerts"]))

        submitted = st.form_submit_button("💾 SAVE SETTINGS")

        if submitted:
            new_settings = {
                "model_path": model_path,
                "confidence_threshold": conf_thresh,
                "buffer_size": buffer_size,
                "detection_ratio": det_ratio,
                "camera_id": camera_id,
                "serial_port": serial_port,
                "baud_rate": baud_rate,
                "simulation_mode": sim_mode,
                "voice_alerts": voice_alerts
            }
            save_settings(new_settings)
            st.session_state.settings = new_settings
            
            # Reload detector and hardware
            st.session_state.detector = HazardDetector(model_path, conf_thresh)
            st.session_state.logic.update_settings(buffer_size, det_ratio)
            st.session_state.arduino = ArduinoController(serial_port, baud_rate, sim_mode)
            
            st.success("Settings saved successfully!")
            st.rerun()

def render_about_page():
    """Renders system documentation and about info."""
    render_header()
    st.subheader("ℹ️ About the Project")

    st.markdown("""
    ### AI Road Hazard Detection & Smart Speed Control System
    An advanced Computer Vision and IoT prototype designed to enhance road safety by early identification of road anomalies (Potholes & Speed Breakers) and broadcasting real-time speed reduction alerts to vehicle hardware controllers.

    #### Key Architecture Features:
    - **Object Detection Engine**: Powered by Ultralytics YOLO11 deep learning model trained on pothole and speed breaker datasets.
    - **Temporal Frame-Buffer Smoothing**: Prevents false positive warnings by requiring consistent multi-frame detection ratios (`deque` buffer).
    - **Hardware Interface**: PySerial integration with Arduino Microcontroller operating RGB status LEDs and buzzer alert system.
    - **Analytics & History**: Persistent CSV history tracking with Plotly statistical visualizations.

    #### Technology Stack:
    - **Language**: Python 3.x
    - **Computer Vision**: OpenCV, Ultralytics YOLO11, PyTorch
    - **Web Framework**: Streamlit
    - **Hardware**: Arduino (C++), PySerial
    - **Visualization**: Plotly, Pandas
    """)
