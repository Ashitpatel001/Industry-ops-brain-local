"""
ui/pages/3_🕸_Knowledge_Graph.py
================================
Interactive PyVis Knowledge Graph Studio for Ops Brain Local.
Visualizes multi-hop industrial relationships between equipment assets, failure modes,
root causes, regulations, and work orders.

GET /api/v1/graph/{target_node}?depth={n}
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

from ui.components.theme import inject_global_css, render_hero, render_section_label
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

inject_global_css()

with st.sidebar:
    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; color:#fff;'>Diagnostics</p>", unsafe_allow_html=True)
    render_model_status()

render_privacy_banner()
render_hero(
    eyebrow="Graph Explorer",
    title="Trace multi-hop relationships across the plant.",
    subtitle="Equipment, failure modes, regulations and work orders as a live network. Drag nodes to explore how a single asset connects to the rest of the plant.",
    sheet_no="OB / 03",
)

API_URL = "http://127.0.0.1:8000"

render_section_label("01", "Graph Filter")

col1, col2 = st.columns([1, 4], gap="large")

with col1:
    target_node = st.text_input("Center node / asset tag", value="all", help="e.g. P-204, HX-301, or 'all' for the full topology.")
    hop_depth = st.slider("Neighborhood depth", min_value=1, max_value=3, value=2)

    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; font-size:0.85rem; margin-top:18px;'>Legend</p>", unsafe_allow_html=True)
    legend = [
        ("#2563EB", "Equipment Asset"),
        ("#C0362C", "Failure Mode"),
        ("#B7791F", "Work Order"),
        ("#12875D", "Regulation / Clause"),
        ("#7C3AED", "Incident / Near Miss"),
    ]
    legend_html = "".join(
        f"<div style='display:flex; align-items:center; gap:8px; font-size:0.83rem; margin-bottom:6px; color:#51607A;'>"
        f"<span style='width:10px; height:10px; border-radius:50%; background:{c};'></span>{l}</div>"
        for c, l in legend
    )
    st.markdown(legend_html, unsafe_allow_html=True)

with col2:
    with st.spinner("Fetching knowledge graph from local SQLite & NetworkX engine..."):
        try:
            resp = requests.get(f"{API_URL}/api/v1/graph/{target_node}", params={"depth": hop_depth}, timeout=10.0)
            if resp.status_code == 200:
                graph_data = resp.json()
                nodes = graph_data.get("nodes", [])
                edges = graph_data.get("edges", [])

                if not nodes:
                    st.warning(f"No knowledge graph nodes found for '{target_node}'. Try 'all' or 'P-204'.")
                else:
                    try:
                        from pyvis.network import Network

                        net = Network(height="640px", width="100%", bgcolor="#FFFFFF", font_color="#0B1F3A", directed=True)
                        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=150, spring_strength=0.08)

                        color_map = {
                            "ASSET": "#2563EB",
                            "FAILURE_MODE": "#C0362C",
                            "WORK_ORDER": "#B7791F",
                            "REGULATION": "#12875D",
                            "INCIDENT": "#7C3AED",
                            "PROCEDURE": "#0D9488",
                        }

                        for n in nodes:
                            n_id = n["id"]
                            n_type = n.get("type", "ASSET").upper()
                            color = color_map.get(n_type, "#94A3B8")
                            title_hover = f"Type: {n_type}\nID: {n_id}\n" + "\n".join(
                                f"{k}: {v}" for k, v in n.items() if k not in ["id", "type", "label"]
                            )
                            net.add_node(n_id, label=str(n_id), title=title_hover, color=color,
                                         size=25 if n_type == "ASSET" else 18)

                        for e in edges:
                            net.add_edge(e["source"], e["target"], title=e.get("relation", ""),
                                         label=e.get("relation", ""), color="rgba(20,49,92,0.25)")

                        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                            net.save_graph(tmp_file.name)
                            tmp_path = tmp_file.name

                        with open(tmp_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        os.unlink(tmp_path)

                        components.html(html_content, height=650, scrolling=False)
                    except ImportError:
                        st.error("`pyvis` package is required for interactive rendering. Please install it or check requirements.")
            else:
                st.error(f"Could not retrieve graph: {resp.text}")
        except Exception as e:
            st.error(f"Connection error to API backend: {e}")
