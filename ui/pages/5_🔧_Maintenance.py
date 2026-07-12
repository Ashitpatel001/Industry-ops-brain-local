"""
ui/pages/5_🔧_Maintenance.py
============================
Maintenance & Reliability Engineering Studio for Ops Brain Local.
Equipment risk matrix (MTBF vs criticality), a work-order generator, and an
interactive 5-Why Root Cause Analysis (RCA) generator — both driven through
POST /api/v1/query with the current payload/response contract.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests

st.set_page_config(page_title="Maintenance & RCA | Ops Brain Local", page_icon="🔧", layout="wide")

from ui.components.theme import inject_global_css, render_hero, render_section_label, status_pill
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status
from ui.components.confidence_badge import render_confidence_badge
from ui.components.citation_card import render_citation_card
from ui.components.actions_checklist import render_actions_checklist

inject_global_css()

with st.sidebar:
    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; color:#fff;'>Diagnostics</p>", unsafe_allow_html=True)
    render_model_status()

render_privacy_banner()
render_hero(
    eyebrow="Maintenance & Reliability",
    title="From symptom to root cause, in one pass.",
    subtitle="Live MTBF risk matrix, CMMS work-order dispatch, and structured 5-Why root cause analysis.",
    sheet_no="OB / 05",
)

API_URL = "http://127.0.0.1:8000"

tab1, tab2, tab3 = st.tabs(["📊 Asset Risk Matrix", "📋 Work Order Generator", "🔍 5-Why Root Cause Analysis"])

# TAB 1: Asset Risk Matrix
with tab1:
    render_section_label("01", "Equipment Reliability Risk Matrix")
    st.markdown(
        "<p style='font-size:0.83rem; color:#8A9BB8;'>Risk score = "
        "<code>(historical failures × criticality factor × 1000) / estimated MTBF hours</code></p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Calculating asset risk scores..."):
        try:
            resp = requests.get(f"{API_URL}/api/v1/assets", timeout=10.0)
            if resp.status_code == 200:
                assets = resp.json().get("assets", [])
                if assets:
                    assets.sort(key=lambda x: x.get("risk_score", 0), reverse=True)

                    for a in assets:
                        tag = a.get("asset_tag", "UNKNOWN")
                        name = a.get("name", "Unnamed asset")
                        score = a.get("risk_score", 0.0)
                        cat = str(a.get("risk_category", "LOW")).upper()
                        unit = a.get("process_unit", "Refinery")

                        tone = "danger" if cat == "HIGH" else ("warning" if cat == "MEDIUM" else "success")
                        accent = {"danger": "#C0362C", "warning": "#B7791F", "success": "#12875D"}[tone]

                        st.markdown(
                            f"""
                            <div style="background:#FFFFFF; border:1px solid #E2E6ED; border-left:5px solid {accent};
                                border-radius:8px; padding:14px 20px; margin-bottom:10px;
                                display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span style="font-family:'IBM Plex Mono',monospace; font-weight:600; font-size:1.02rem; color:#14315C;">{tag}</span>
                                    <span style="font-weight:600; color:#0B1F3A; margin-left:10px;">{name}</span><br>
                                    <span style="font-size:0.8rem; color:#8A9BB8;">Unit: {unit} &middot; MTBF: {a.get('mtbf_days', 100)} days &middot; Status: {a.get('status', 'OK')}</span>
                                </div>
                                <div style="text-align:right;">
                                    <div style="font-family:'IBM Plex Mono',monospace; font-size:1.3rem; font-weight:700; color:{accent};">{score}</div>
                                    {status_pill(f"RISK: {cat}", tone)}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No plant assets indexed.")
            else:
                st.error(f"Could not retrieve assets: {resp.text}")
        except Exception as e:
            st.error(f"Error communicating with backend API: {e}")

# TAB 2: Work Order Generator
with tab2:
    render_section_label("02", "Create & Dispatch Work Order")

    col_a, col_b = st.columns(2)
    with col_a:
        wo_asset = st.text_input("Asset tag", value="P-204", help="Equipment tag requiring maintenance")
        wo_priority = st.selectbox("Priority level", ["HIGH", "CRITICAL", "EMERGENCY", "MEDIUM", "LOW"])
    with col_b:
        wo_failure = st.text_input("Failure mode / symptom", value="Mechanical seal leakage and high bearing vibration")
        wo_desc = st.text_area("Detailed problem description",
                                value="Primary mechanical seal showing 15 drops/min leak rate. 1X RPM vibration spike detected on drive-end bearing.")

    if st.button("🚀 Generate & Persist Work Order"):
        with st.spinner("Dispatching to local CMMS database..."):
            try:
                payload = {
                    "text": f"Create work order for {wo_asset} due to {wo_failure}. Priority: {wo_priority}. Description: {wo_desc}",
                    "intent": "maintenance",
                    "asset_tags": [wo_asset],
                }
                resp = requests.post(f"{API_URL}/api/v1/query", json=payload, timeout=180.0)
                if resp.status_code == 200:
                    res_data = resp.json()
                    st.success("Work order created and stored.")
                    render_confidence_badge(res_data.get("confidence", "MEDIUM"))
                    st.markdown("#### 📝 AI Maintenance Engineering Summary")
                    st.markdown(res_data.get("answer", ""))
                    render_actions_checklist(res_data.get("recommended_actions", []), key_prefix="wo")
                    render_citation_card(res_data.get("citations", []))
                else:
                    st.error(f"Failed to generate work order: {resp.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# TAB 3: 5-Why Root Cause Analysis
with tab3:
    render_section_label("03", "Automated 5-Why Root Cause Analysis")
    rca_asset = st.text_input("Target asset tag for RCA", value="P-204")
    rca_symptom = st.text_input("Primary failure mode", value="Mechanical seal face thermal distortion and leakage")

    if st.button("🔬 Execute 5-Why Analysis"):
        with st.spinner("Traversing knowledge graph failure chains..."):
            try:
                payload = {
                    "text": f"Generate a 5-Why RCA for {rca_asset} regarding {rca_symptom}",
                    "intent": "maintenance",
                    "asset_tags": [rca_asset],
                }
                resp = requests.post(f"{API_URL}/api/v1/query", json=payload, timeout=180.0)
                if resp.status_code == 200:
                    res_data = resp.json()
                    st.success(f"Root cause analysis complete for {rca_asset}")
                    render_confidence_badge(res_data.get("confidence", "MEDIUM"))
                    st.markdown(res_data.get("answer", ""))
                    render_actions_checklist(res_data.get("recommended_actions", []), key_prefix="rca")
                    render_citation_card(res_data.get("citations", []))
                else:
                    st.error(f"RCA failed: {resp.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
