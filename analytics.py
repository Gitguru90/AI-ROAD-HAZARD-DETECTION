import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.history import load_history

def get_analytics_summary(df=None):
    """Calculates summary stats from detection history dataframe."""
    if df is None:
        df = load_history()
    
    if df.empty:
        return {
            "total_hazards": 0,
            "potholes": 0,
            "speed_breakers": 0,
            "avg_confidence": "0%"
        }
    
    potholes = len(df[df["Hazard"].str.contains("Pothole", case=False, na=False)])
    speed_breakers = len(df[df["Hazard"].str.contains("Speed", case=False, na=False)])
    total = len(df)
    
    # Calculate numeric confidence average
    try:
        conf_vals = df["Confidence"].astype(str).str.rstrip('%').astype(float)
        avg_conf = f"{int(conf_vals.mean())}%"
    except Exception:
        avg_conf = "N/A"

    return {
        "total_hazards": total,
        "potholes": potholes,
        "speed_breakers": speed_breakers,
        "avg_confidence": avg_conf
    }

def create_hazard_pie_chart(df=None):
    """Donut chart comparing Potholes vs Speed Breakers."""
    if df is None:
        df = load_history()
    
    summary = get_analytics_summary(df)
    labels = ["Potholes", "Speed Breakers"]
    values = [summary["potholes"], summary["speed_breakers"]]

    if sum(values) == 0:
        # Placeholder empty pie chart
        fig = go.Figure(go.Pie(labels=["No Data"], values=[1], hole=0.5, marker=dict(colors=["#334155"])))
        fig.update_layout(title_text="Hazard Breakdown", template="plotly_dark")
        return fig

    fig = px.pie(
        names=labels,
        values=values,
        hole=0.5,
        color=labels,
        color_discrete_map={"Potholes": "#EF4444", "Speed Breakers": "#F59E0B"},
        title="Hazard Type Breakdown"
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def create_confidence_histogram(df=None):
    """Histogram of confidence scores."""
    if df is None:
        df = load_history()

    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Confidence Score Distribution (No Data)", template="plotly_dark")
        return fig

    try:
        df_plot = df.copy()
        df_plot["Conf_Val"] = df_plot["Confidence"].astype(str).str.rstrip('%').astype(float)
        fig = px.histogram(
            df_plot,
            x="Conf_Val",
            color="Hazard",
            nbins=15,
            color_discrete_map={"Pothole": "#EF4444", "Speed Breaker": "#F59E0B"},
            labels={"Conf_Val": "Confidence (%)"},
            title="Detection Confidence Distribution"
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
    except Exception:
        fig = go.Figure()
        fig.update_layout(title="Confidence Distribution", template="plotly_dark")
        return fig

def create_timeline_chart(df=None):
    """Scatter/Line plot of hazards over time."""
    if df is None:
        df = load_history()

    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Detections Over Time (No Data)", template="plotly_dark")
        return fig

    try:
        df_plot = df.copy()
        df_plot["Conf_Val"] = df_plot["Confidence"].astype(str).str.rstrip('%').astype(float)
        fig = px.scatter(
            df_plot,
            x="Timestamp",
            y="Conf_Val",
            color="Hazard",
            size="Conf_Val",
            hover_data=["Frame", "Video"],
            color_discrete_map={"Pothole": "#EF4444", "Speed Breaker": "#F59E0B"},
            title="Detections Over Time"
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Time",
            yaxis_title="Confidence (%)"
        )
        return fig
    except Exception:
        fig = go.Figure()
        fig.update_layout(title="Detections Over Time", template="plotly_dark")
        return fig

def create_video_source_chart(df=None):
    """Bar chart counting detections per video source."""
    if df is None:
        df = load_history()

    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="Detections by Source (No Data)", template="plotly_dark")
        return fig

    try:
        source_counts = df.groupby(["Video", "Hazard"]).size().reset_index(name="Count")
        fig = px.bar(
            source_counts,
            x="Video",
            y="Count",
            color="Hazard",
            barmode="group",
            color_discrete_map={"Pothole": "#EF4444", "Speed Breaker": "#F59E0B"},
            title="Hazard Detections by Source"
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig
    except Exception:
        fig = go.Figure()
        fig.update_layout(title="Detections by Source", template="plotly_dark")
        return fig
