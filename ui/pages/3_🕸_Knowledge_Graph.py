"""
ui/pages/3_🕸_Knowledge_Graph.py
================================
Interactive PyVis Knowledge Graph Studio for Ops Brain Local.
Visualizes multi-hop industrial relationships between equipment assets, failure modes,
root causes, regulations, and work orders.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests
import tempfile
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Knowledge Graph | Ops Brain Local", page_icon="🕸️", layout="wide")

from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

render_privacy_banner()

with st.sidebar:
    st.markdown("### Diagnostics")
    render_model_status()

st.markdown("<h1 style='color: #38BDF8;'>🕸️ Industrial Knowledge Graph Explorer</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Interactive network topology of refinery equipment, failure modes, regulations, and work orders. Click and drag nodes to explore multi-hop operational relationships.</p>", unsafe_allow_html=True)
st.markdown("---")

API_URL = "http://127.0.0.1:8000"

col1, col2 = st.columns([1, 4])

with col1:
    st.markdown("### Graph Filter")
    target_node = st.text_input("Center Node / Asset Tag", value="all", help="Enter an asset tag (e.g. P-204, HX-301) or 'all' to view the full topology.")
    hop_depth = st.slider("Neighborhood Depth", min_value=1, max_value=3, value=2)
    
    st.markdown("### Legend")
    st.markdown(
        """
        <style>
        .leg-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; margin-bottom: 6px; }
        .leg-dot { width: 12px; height: 12px; border-radius: 50%; }
        </style>
        <div class="leg-item"><div class="leg-dot" style="background: #0EA5E9;"></div><span>Equipment Asset</span></div>
        <div class="leg-item"><div class="leg-dot" style="background: #EF4444;"></div><span>Failure Mode</span></div>
        <div class="leg-item"><div class="leg-dot" style="background: #F59E0B;"></div><span>Work Order</span></div>
        <div class="leg-item"><div class="leg-dot" style="background: #10B981;"></div><span>Regulation / Clause</span></div>
        <div class="leg-item"><div class="leg-dot" style="background: #8B5CF6;"></div><span>Incident / Near Miss</span></div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    with st.spinner("Fetching knowledge graph from local SQLite & NetworkX engine..."):
        try:
            resp = requests.get(f"{API_URL}/api/v1/graph/{target_node}?depth={hop_depth}", timeout=10.0)
            if resp.status_code == 200:
                graph_data = resp.json()
                nodes = graph_data.get("nodes", [])
                edges = graph_data.get("edges", [])
                
                if not nodes:
                    st.warning(f" No knowledge graph nodes found for '{target_node}'. Try searching for 'all' or 'P-204'.")
                else:
                    try:
                        from pyvis.network import Network
                        
                        net = Network(height="650px", width="100%", bgcolor="#0F172A", font_color="#F8FAFC", directed=True)
                        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=150, spring_strength=0.08)
                        
                        color_map = {
                            "ASSET": "#0EA5E9",
                            "FAILURE_MODE": "#EF4444",
                            "WORK_ORDER": "#F59E0B",
                            "REGULATION": "#10B981",
                            "INCIDENT": "#8B5CF6",
                            "PROCEDURE": "#34D399",
                        }
                        
                        for n in nodes:
                            n_id = n["id"]
                            n_type = n.get("type", "ASSET").upper()
                            color = color_map.get(n_type, "#94A3B8")
                            title_hover = f"Type: {n_type}\nID: {n_id}\n" + "\n".join(f"{k}: {v}" for k, v in n.items() if k not in ["id", "type", "label"])
                            net.add_node(n_id, label=str(n_id), title=title_hover, color=color, size=25 if n_type == "ASSET" else 18)
                            
                        for e in edges:
                            src = e["source"]
                            tgt = e["target"]
                            rel = e.get("relation", "")
                            net.add_edge(src, tgt, title=rel, label=rel, color="rgba(148, 163, 184, 0.4)")
                            
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                            net.save_graph(tmp_file.name)
                            tmp_path = tmp_file.name
                            
                        with open(tmp_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        os.unlink(tmp_path)
                        
                        components.html(html_content, height=660, scrolling=False)
                    except ImportError:
                        st.error(" `pyvis` package is required for interactive rendering. Please install it or check requirements.")
            else:
                st.error(f" Could not retrieve graph: {resp.text}")
        except Exception as e:
            st.error(f" Connection error to API backend: {e}")
