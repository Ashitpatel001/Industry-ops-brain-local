"""
ui/pages/5_🔧_Maintenance.py
============================
Specialized Maintenance & Reliability Engineering Studio for Ops Brain Local.
Presents equipment reliability risk scores (MTBF vs Criticality), open Work Orders,
and interactive 5-Why Root Cause Analysis (RCA) generators.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests
import json

st.set_page_config(page_title="Maintenance & RCA | Ops Brain Local", page_icon="🔧", layout="wide")

from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

render_privacy_banner()

with st.sidebar:
    st.markdown("### ⚡ Diagnostics")
    render_model_status()

st.markdown("<h1 style='color: #F59E0B;'>🔧 Maintenance & Reliability Command Center</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Real-time MTBF reliability risk matrix, automated CMMS Work Order dispatch, and structured 5-Why Root Cause Analysis (RCA) generation.</p>", unsafe_allow_html=True)
st.markdown("---")

API_URL = "http://127.0.0.1:8000"

tab1, tab2, tab3 = st.tabs(["📊 Asset Risk Matrix", "📋 Work Order Generator", "🔍 5-Why Root Cause Analysis"])

# TAB 1: Asset Risk Matrix
with tab1:
    st.markdown("### ⚡ Equipment Reliability Risk Matrix")
    st.markdown("<p style='font-size: 0.85rem; color: #94A3B8;'>Risk Score computed as: <code>(Historical Failures * Criticality Factor * 1000) / Estimated MTBF Hours</code></p>", unsafe_allow_html=True)
    
    with st.spinner("⏳ Calculating asset risk scores..."):
        try:
            resp = requests.get(f"{API_URL}/api/v1/assets", timeout=10.0)
            if resp.status_code == 200:
                assets = resp.json().get("assets", [])
                if assets:
                    # Sort by risk score descending
                    assets.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
                    
                    for a in assets:
                        tag = a.get("asset_tag", "UNKNOWN")
                        name = a.get("name", "Unnamed Asset")
                        score = a.get("risk_score", 0.0)
                        cat = a.get("risk_category", "LOW")
                        unit = a.get("process_unit", "Refinery")
                        
                        badge_color = "#EF4444" if cat == "HIGH" else ("#F59E0B" if cat == "MEDIUM" else "#10B981")
                        
                        st.markdown(
                            f"""
                            <style>
                            .asset-card {{
                                background: rgba(30, 41, 59, 0.7);
                                border: 1px solid rgba(148, 163, 184, 0.2);
                                border-left: 5px solid {badge_color};
                                padding: 14px 18px;
                                border-radius: 8px;
                                margin-bottom: 12px;
                                display: flex;
                                justify-content: space-between;
                                align-items: center;
                                font-family: 'Inter', sans-serif;
                            }}
                            </style>
                            <div class="asset-card">
                                <div>
                                    <span style="font-family: 'Outfit'; font-weight: 700; font-size: 1.1rem; color: #38BDF8;">{tag}</span>
                                    <span style="font-weight: 600; color: #E2E8F0; margin-left: 10px;">{name}</span><br>
                                    <span style="font-size: 0.8rem; color: #94A3B8;">Unit: {unit} | MTBF: {a.get('mtbf_days', 100)} Days | Status: {a.get('status', 'OK')}</span>
                                </div>
                                <div style="text-align: right;">
                                    <span style="font-size: 1.4rem; font-weight: 700; color: {badge_color};">{score}</span><br>
                                    <span style="background: {badge_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 700;">RISK: {cat}</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No plant assets indexed.")
        except Exception as e:
            st.error(f"❌ Error communicating with backend API: {e}")

# TAB 2: Work Order Generator
with tab2:
    st.markdown("### 📋 Create & Dispatch Industrial Work Order")
    
    col_a, col_b = st.columns(2)
    with col_a:
        wo_asset = st.text_input("Asset Tag", value="P-204", help="Equipment tag requiring maintenance")
        wo_priority = st.selectbox("Priority Level", ["HIGH", "CRITICAL", "EMERGENCY", "MEDIUM", "LOW"])
    with col_b:
        wo_failure = st.text_input("Failure Mode / Symptom", value="Mechanical seal leakage and high bearing vibration")
        wo_desc = st.text_area("Detailed Problem Description", value="Primary mechanical seal showing 15 drops/min leak rate. 1X RPM vibration spike detected on drive-end bearing.")
        
    if st.button("🚀 Generate & Persist Work Order"):
        with st.spinner("⏳ Dispatching to local SQLite CMMS database..."):
            try:
                # Trigger maintenance agent via query endpoint
                payload = {
                    "query": f"Create work order for {wo_asset} due to {wo_failure}. Priority: {wo_priority}. Description: {wo_desc}",
                    "intent": "maintenance",
                    "asset_tags": [wo_asset]
                }
                resp = requests.post(f"{API_URL}/api/v1/query", json=payload, timeout=180.0)
                if resp.status_code == 200:
                    res_data = resp.json()
                    st.success(f"✅ Work Order successfully created and stored in SQLite database!")
                    st.markdown("#### 📝 AI Maintenance Engineering Summary:")
                    st.markdown(res_data.get("answer", ""))
                else:
                    st.error(f"❌ Failed to generate WO: {resp.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")

# TAB 3: 5-Why Root Cause Analysis
with tab3:
    st.markdown("### 🔍 Automated 5-Why Root Cause Analysis (RCA)")
    rca_asset = st.text_input("Target Asset Tag for RCA", value="P-204")
    rca_symptom = st.text_input("Primary Failure Mode", value="Mechanical seal face thermal distortion and leakage")
    
    if st.button("🔬 Execute 5-Why Analysis"):
        with st.spinner("⏳ Traversing knowledge graph failure chains..."):
            try:
                payload = {
                    "query": f"Generate 5 why RCA for {rca_asset} regarding {rca_symptom}",
                    "intent": "maintenance",
                    "asset_tags": [rca_asset]
                }
                resp = requests.post(f"{API_URL}/api/v1/query", json=payload, timeout=180.0)
                if resp.status_code == 200:
                    res_data = resp.json()
                    st.success(f"✅ Root Cause Analysis Complete for **{rca_asset}**!")
                    st.markdown(res_data.get("answer", ""))
                else:
                    st.error(f"❌ RCA failed: {resp.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
