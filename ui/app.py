"""
ui/app.py
=========
Main entry point for the Ops Brain Local Streamlit Application.
Sets up global glassmorphic dark-mode CSS, renders offline air-gapped security banners,
displays real-time hardware acceleration status in the sidebar, and presents an executive dashboard.

Run app:
    streamlit run ui/app.py
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests

# Configure global Streamlit page settings
st.set_page_config(
    page_title="Ops Brain Local | Industrial AI Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import custom reusable components
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

# --- Global Glassmorphic Dark Mode CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Typography & Backgrounds */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #F8FAFC;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(15, 23, 42) 0%, rgb(10, 15, 30) 90%);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Sleek Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #CBD5E1;
    }

    /* Glassmorphic Metric & Info Cards */
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #38BDF8 0%, #10B981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        line-height: 1.6;
    }

    /* Custom Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0EA5E9 0%, #10B981 100%);
        color: white;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }

    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Render Top-Bar Air-Gapped Security Banner
render_privacy_banner()

# Render Sidebar Diagnostics
with st.sidebar:
    st.markdown("<h2 style='font-family: Outfit; color: #38BDF8;'>⚡ Ops Brain Local</h2>", unsafe_allow_html=True)
    st.markdown("---")
    render_model_status()
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.8rem; color: #64748B; text-align: center;">
            <strong>OSDHack 2026 Winning Architecture</strong><br>
            100% On-Premise Industrial RAG Engine
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Executive Landing Dashboard ---
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Welcome to Ops Brain Local</div>
        <div class="hero-subtitle">
            The next-generation, air-gapped AI operations command center designed specifically for refineries, chemical plants, and heavy manufacturing facilities.
            Powered by hardware-accelerated OpenVINO INT4 models and multi-agent collaborative reasoning, Ops Brain Local turns complex industrial data into instant, actionable reliability decisions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Quick Navigation Grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2); height: 100%;">
            <h3 style="color: #38BDF8; margin-bottom: 10px;">💬 Ask Plant Co-Pilot</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">Execute natural language queries against plant SOPs, engineering drawings, and historical maintenance logs with instant verified citations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2); height: 100%;">
            <h3 style="color: #10B981; margin-bottom: 10px;">🔧 Maintenance & RCA</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">Automate 5-Why Root Cause Analyses, compute real-time MTBF reliability risk scores, and generate persistent CMMS Work Orders.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.2); height: 100%;">
            <h3 style="color: #F59E0B; margin-bottom: 10px;">🛡️ Compliance Audit</h3>
            <p style="color: #94A3B8; font-size: 0.9rem;">Verify plant operations against OISD-116, Factory Act 1948, and PESO rules using deterministic Evidence Matrix gap detection.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.markdown("<h4 style='color: #E2E8F0;'>👈 Select a module from the sidebar navigation to get started.</h4>", unsafe_allow_html=True)
