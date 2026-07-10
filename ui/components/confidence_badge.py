"""
ui/components/confidence_badge.py
Renders a glowing glassmorphic confidence badge (HIGH, MEDIUM, LOW)
with tailored color palettes and micro-animations.
"""

import streamlit as st


def render_confidence_badge(confidence: str = "MEDIUM"):
    """Render an aesthetic confidence badge."""
    conf_upper = (confidence or "MEDIUM").upper()
    
    if conf_upper == "HIGH":
        bg_color = "rgba(16, 185, 129, 0.15)"
        border_color = "rgba(16, 185, 129, 0.4)"
        text_color = "#34D399"
        icon = "🟢"
    elif conf_upper == "LOW":
        bg_color = "rgba(239, 68, 68, 0.15)"
        border_color = "rgba(239, 68, 68, 0.4)"
        text_color = "#F87171"
        icon = "🔴"
    else:
        bg_color = "rgba(245, 158, 11, 0.15)"
        border_color = "rgba(245, 158, 11, 0.4)"
        text_color = "#FBBF24"
        icon = "🟡"

    st.markdown(
        f"""
        <style>
        .conf-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: {bg_color};
            border: 1px solid {border_color};
            color: {text_color};
            padding: 4px 12px;
            border-radius: 20px;
            font-family: 'Outfit', sans-serif;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease;
        }}
        .conf-badge:hover {{
            transform: scale(1.05);
        }}
        </style>
        <div class="conf-badge">
            <span>{icon}</span>
            <span>CONFIDENCE: {conf_upper}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )