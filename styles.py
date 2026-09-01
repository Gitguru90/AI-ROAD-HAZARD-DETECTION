"""
Modern sleek dark CSS design system for Streamlit UI.
"""

CSS_STYLES = """
<style>
/* Main Dark Theme Styling */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0F172A;
    color: #F8FAFC;
}

/* Glassmorphism Header Card */
.main-header-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.main-header-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.02em;
}

.main-header-subtitle {
    color: #94A3B8;
    font-size: 0.95rem;
    font-weight: 400;
    margin-top: 6px;
}

/* Status Cards */
.stat-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
    border-color: #38BDF8;
}

.stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-top: 4px;
}

.stat-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Hazard Alert Status Panels */
.status-panel-clear {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 78, 59, 0.3));
    border: 2px solid #10B981;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
}

.status-panel-pothole {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(127, 29, 29, 0.4));
    border: 2px solid #EF4444;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    animation: pulse-red 2s infinite;
    box-shadow: 0 0 25px rgba(239, 68, 68, 0.35);
}

.status-panel-speedbreaker {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(120, 53, 15, 0.4));
    border: 2px solid #F59E0B;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    animation: pulse-amber 2s infinite;
    box-shadow: 0 0 25px rgba(245, 158, 11, 0.35);
}

.status-title-large {
    font-size: 1.6rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.status-action-pill {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    margin-top: 10px;
}

.pill-clear { background-color: #10B981; color: #042F2E; }
.pill-pothole { background-color: #EF4444; color: #FFF; }
.pill-speedbreaker { background-color: #F59E0B; color: #1C1917; }

/* Status Pill Indicators for Sidebar */
.indicator-pill {
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 6px;
    background: #1E293B;
    border: 1px solid #334155;
}

/* Custom Table Styling */
.dataframe {
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Animations */
@keyframes pulse-red {
    0% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }
    50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.5); }
    100% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }
}

@keyframes pulse-amber {
    0% { box-shadow: 0 0 15px rgba(245, 158, 11, 0.2); }
    50% { box-shadow: 0 0 30px rgba(245, 158, 11, 0.5); }
    100% { box-shadow: 0 0 15px rgba(245, 158, 11, 0.2); }
}
</style>
"""

def apply_custom_styles():
    """Returns Markdown component to inject CSS styles."""
    import streamlit as st
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
