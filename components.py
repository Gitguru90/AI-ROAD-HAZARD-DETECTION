import streamlit as st

def render_header():
    """Renders main application header card."""
    html = """
    <div class="main-header-card">
        <h1 class="main-header-title">🚗 AI ROAD HAZARD DETECTION</h1>
        <div class="main-header-subtitle">SMART SPEED CONTROL SYSTEM &bull; Real-Time Computer Vision & IoT Safety</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_sidebar_status(model_loaded=False, hardware_status=("Simulation", "🟡"), camera_available=True):
    """Renders system status indicators in the Streamlit sidebar."""
    st.sidebar.markdown("### System Status")
    
    # Model Status
    model_str = "🟢 Loaded" if model_loaded else "🔴 Demo / Not Loaded"
    st.sidebar.markdown(f"**AI Model:** {model_str}")
    
    # Arduino Status
    hw_str, hw_icon = hardware_status
    st.sidebar.markdown(f"**Arduino:** {hw_icon} {hw_str}")
    
    # Camera Status
    cam_str = "🟢 Available" if camera_available else "🔴 Not Available"
    st.sidebar.markdown(f"**Camera:** {cam_str}")
    
    # Detection Engine
    st.sidebar.markdown("**Detection:** 🟢 Ready")
    st.sidebar.markdown("---")

def render_stat_card(label, value, icon="📊"):
    """Returns HTML string for a single stat card."""
    return f"""
    <div class="stat-card">
        <div style="font-size: 1.5rem; margin-bottom: 4px;">{icon}</div>
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
    </div>
    """

def render_status_panel(hazard_state):
    """
    Renders right-side prominent status alert panel depending on hazard state.
    """
    status = hazard_state.get("status", "NORMAL")
    conf = hazard_state.get("confidence", 0.0)
    conf_pct = int(conf * 100)

    if status == "POTHOLE":
        html = f"""
        <div class="status-panel-pothole">
            <div style="font-size: 3rem; margin-bottom: 8px;">🕳️</div>
            <div class="status-title-large" style="color: #EF4444;">POTHOLE DETECTED</div>
            <div style="font-size: 1.1rem; color: #FCA5A5; font-weight: 600;">Confidence: {conf_pct}%</div>
            <div class="status-action-pill pill-pothole">⚠️ REDUCE SPEED</div>
        </div>
        """
    elif status == "SPEED_BREAKER":
        html = f"""
        <div class="status-panel-speedbreaker">
            <div style="font-size: 3rem; margin-bottom: 8px;">🚧</div>
            <div class="status-title-large" style="color: #F59E0B;">SPEED BREAKER DETECTED</div>
            <div style="font-size: 1.1rem; color: #FDE68A; font-weight: 600;">Confidence: {conf_pct}%</div>
            <div class="status-action-pill pill-speedbreaker">⚠️ REDUCE SPEED</div>
        </div>
        """
    else:
        html = """
        <div class="status-panel-clear">
            <div style="font-size: 3rem; margin-bottom: 8px;">🟢</div>
            <div class="status-title-large" style="color: #10B981;">ROAD CLEAR</div>
            <div style="font-size: 1.1rem; color: #A7F3D0; font-weight: 600;">Conditions Normal</div>
            <div class="status-action-pill pill-clear">NORMAL SPEED</div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)

def render_hazard_detail_card(hazard_state, frame_idx=0, time_str="00:00"):
    """Renders bottom detail card for active hazard."""
    status = hazard_state.get("status", "NORMAL")
    conf = hazard_state.get("confidence", 0.0)
    conf_pct = f"{int(conf * 100)}%" if conf > 0 else "N/A"
    
    if status == "POTHOLE":
        h_type = "Pothole"
        action = "Reduce Speed"
        det_status = "Confirmed"
    elif status == "SPEED_BREAKER":
        h_type = "Speed Breaker"
        action = "Reduce Speed"
        det_status = "Confirmed"
    else:
        h_type = "None"
        action = "Normal Speed"
        det_status = "Clear"

    html = f"""
    <div style="background: #1E293B; border-radius: 12px; padding: 18px; border: 1px solid #334155; margin-top: 15px;">
        <h4 style="margin-top: 0; color: #38BDF8; font-size: 1.1rem;">Current Hazard Info</h4>
        <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; text-align: center;">
            <div>
                <span style="color: #94A3B8; font-size: 0.8rem;">TYPE</span>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 2px;">{h_type}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.8rem;">CONFIDENCE</span>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 2px;">{conf_pct}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.8rem;">STATUS</span>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 2px;">{det_status}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.8rem;">ACTION</span>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 2px;">{action}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.8rem;">FRAME</span>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 2px;">#{frame_idx}</div>
            </div>
            <div>
                <span style="color: #94A3B8; font-size: 0.8rem;">TIME</span>
                <div style="font-weight: 700; color: #F8FAFC; margin-top: 2px;">{time_str}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
