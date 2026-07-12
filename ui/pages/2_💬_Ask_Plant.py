"""
ui/pages/2_💬_Ask_Plant.py
==========================
Interactive Plant Co-Pilot & Multi-Agent Chat interface.
Supports natural language reasoning, intent routing, asset-tag filtering,
confidence badges, an actions checklist, and interactive citation cards.

POST /api/v1/query payload:
    {"text": "...", "intent": "general", "asset_tags": ["TAG-101"]}

Response:
    {"answer": "...", "citations": [...], "confidence": "HIGH",
     "recommended_actions": [...], "metadata": {...}}
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests

st.set_page_config(page_title="Plant Co-Pilot | Ops Brain Local", page_icon="💬", layout="wide")

from ui.components.theme import inject_global_css, render_hero, asset_tag_chip
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status
from ui.components.confidence_badge import render_confidence_badge
from ui.components.citation_card import render_citation_card
from ui.components.actions_checklist import render_actions_checklist

inject_global_css()

with st.sidebar:
    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; color:#fff;'>Diagnostics</p>", unsafe_allow_html=True)
    render_model_status()
    st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; color:#fff; font-size:0.85rem;'>Agent Routing</p>", unsafe_allow_html=True)
    selected_intent = st.selectbox(
        "Target domain agent",
        ["general", "maintenance", "compliance", "lessons"],
        format_func=lambda x: {
            "general": "💬 Copilot (General)",
            "maintenance": "🔧 Maintenance Engineering",
            "compliance": "🛡️ Regulatory Compliance",
            "lessons": "📚 Reliability & Lessons",
        }[x],
        help="Route the query to a specialised domain agent.",
    )
    asset_tags_raw = st.text_input("Asset tags (comma-separated)", value="", placeholder="P-204, HX-301")

render_privacy_banner()
render_hero(
    eyebrow="Plant Co-Pilot",
    title="Ask anything about the plant.",
    subtitle="Complex operational, maintenance or safety questions — answered from SOPs and knowledge-graph nodes, with verified citations attached.",
    sheet_no="OB / 02",
)

API_URL = "http://127.0.0.1:8000"

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I'm your offline Ops Brain Co-Pilot. Ask me about refinery pumps, work orders, safety compliance, or SOP procedures."}
    ]

if asset_tags_raw.strip():
    chips = " ".join(asset_tag_chip(t.strip()) for t in asset_tags_raw.split(",") if t.strip())
    st.markdown(f"<div style='margin-bottom:10px;'>Scoped to: {chips}</div>", unsafe_allow_html=True)

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "citations" in msg and msg["citations"]:
            render_citation_card(msg["citations"])
        if "confidence" in msg:
            render_confidence_badge(msg["confidence"])
        if "actions" in msg and msg["actions"]:
            render_actions_checklist(msg["actions"], key_prefix=f"hist_{id(msg)}")

# Chat Input Area
if prompt := st.chat_input("Ex: Why did P-204's mechanical seal fail? What does OISD-116 require here?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*Synthesizing verified industrial answer from RAG pipeline & graph...*")

        try:
            asset_tags = [t.strip() for t in asset_tags_raw.split(",") if t.strip()]
            payload = {
                "text": prompt,
                "intent": selected_intent,
                "asset_tags": asset_tags,
            }
            resp = requests.post(f"{API_URL}/api/v1/query", json=payload, timeout=180.0)

            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "No answer generated.")
                citations = data.get("citations", [])
                confidence = data.get("confidence", "MEDIUM")
                actions = data.get("recommended_actions", [])
                metadata = data.get("metadata", {})

                message_placeholder.markdown(answer)
                render_confidence_badge(confidence)
                render_citation_card(citations)
                render_actions_checklist(actions, key_prefix=f"new_{len(st.session_state['messages'])}")

                if metadata:
                    st.markdown(
                        f"""
                        <div style="margin-top:10px; font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#8A9BB8;">
                            backend: {metadata.get('backend', '—')} &middot;
                            chunks: {metadata.get('chunks_retrieved', 0)} &middot;
                            graph nodes: {metadata.get('graph_nodes_referenced', 0)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                    "confidence": confidence,
                    "actions": actions,
                })
            else:
                err_msg = f"API error: {resp.status_code} — {resp.text}"
                message_placeholder.error(err_msg)
                st.session_state["messages"].append({"role": "assistant", "content": err_msg})
        except Exception as e:
            err_msg = f"Could not connect to the local backend API: {e}. Make sure `uvicorn api.app:app` is running on port 8000."
            message_placeholder.error(err_msg)
            st.session_state["messages"].append({"role": "assistant", "content": err_msg})
