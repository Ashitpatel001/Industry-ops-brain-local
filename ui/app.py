"""
ui/app.py
=========
Main entry point for the Ops Brain Local Streamlit Application.
Sets up the global light "engineering sheet" design system, renders the
offline air-gapped status strip, live hardware diagnostics in the sidebar,
and an executive landing dashboard.

Run app:
    streamlit run ui/app.py
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st

# Configure global Streamlit page settings
st.set_page_config(
    page_title="Ops Brain Local | Industrial AI Engine",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.components.theme import inject_global_css, render_hero, render_section_label, asset_tag_chip
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

inject_global_css()

# Render Sidebar Diagnostics
with st.sidebar:
    st.markdown(
        "<div style='font-family:Space Grotesk; font-weight:700; font-size:1.15rem; color:#fff; padding:4px 0 2px 0;'>"
        "⚙️ Ops Brain Local</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='font-family:IBM Plex Mono; font-size:0.68rem; color:#9AABC9; margin-bottom:14px;'>"
        "INDUSTRIAL AI ENGINE &middot; v1.0</div>",
        unsafe_allow_html=True,
    )
    render_model_status()
    st.markdown(
        """
        <div style="font-size: 0.72rem; color: #9AABC9; text-align: center; margin-top: 8px; line-height:1.5;">
            <strong style="color:#C6D0E2;">OSDHack 2026 Winning Architecture</strong><br>
            100% on-premise industrial RAG engine
        </div>
        """,
        unsafe_allow_html=True,
    )

# Render Top-Bar Air-Gapped Status Strip
render_privacy_banner()

# --- Executive Landing Dashboard ---
render_hero(
    eyebrow="Ops Brain Local · Command Center",
    title="Welcome back to the plant floor, digitised.",
    subtitle=(
        "An air-gapped operations command center for refineries, chemical plants and heavy "
        "manufacturing sites — hardware-accelerated, multi-agent reasoning turning SOPs, "
        "inspection logs and engineering drawings into instant, verifiable reliability decisions."
    ),
    sheet_no="OB / HOME",
)

render_section_label("01", "Choose a Module")

col1, col2, col3 = st.columns(3)

modules = [
    (col1, "💬", "Ask Plant Co-Pilot",
     "Query SOPs, engineering drawings and maintenance history in plain language, with verified citations attached to every answer.",
     "#2563EB"),
    (col2, "🔧", "Maintenance & RCA",
     "Run 5-Why root cause analyses, track MTBF-based risk scores, and dispatch CMMS work orders straight from a finding.",
     "#12875D"),
    (col3, "🛡️", "Compliance Audit",
     "Check plant operations against OISD-116, the Factory Act 1948 and PESO rules with deterministic evidence-matrix gap detection.",
     "#B7791F"),
]

for col, icon, title, desc, accent in modules:
    with col:
        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E6ED; border-top:3px solid {accent};
                border-radius:10px; padding:22px; height:190px; box-shadow: 0 1px 2px rgba(11,31,58,0.04);">
                <div style="font-size:1.6rem; margin-bottom:10px;">{icon}</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.05rem;
                    color:#0B1F3A; margin-bottom:8px;">{title}</div>
                <div style="color:#51607A; font-size:0.87rem; line-height:1.5;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

render_section_label("02", "Working with Asset Tags")

st.markdown(
    f"""
    <div style="background:#FFFFFF; border:1px solid #E2E6ED; border-radius:10px; padding:18px 22px;
        display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
        <span style="color:#51607A; font-size:0.87rem;">Every module recognises plant asset tags, e.g.</span>
        {asset_tag_chip("P-204")} {asset_tag_chip("HX-301")} {asset_tag_chip("V-118")}
        <span style="color:#51607A; font-size:0.87rem;"> &mdash; use them in the Co-Pilot or Maintenance module to scope an answer to one piece of equipment.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#8A9BB8; font-size:0.85rem;'>👈 Select a module from the sidebar navigation to get started.</p>",
    unsafe_allow_html=True,
)
