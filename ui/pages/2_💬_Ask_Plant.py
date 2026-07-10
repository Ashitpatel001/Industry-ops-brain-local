"""
ui/pages/2_💬_Ask_Plant.py
==========================
Interactive Plant Co-Pilot & Multi-Agent Chat interface.
Supports real-time natural language reasoning, intent routing, equipment tag filtering,
confidence badges, and interactive citation expansion.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests
import json

st.set_page_config(page_title="Plant Co-Pilot | Ops Brain Local", page_icon="💬", layout="wide")

from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status
from ui.components.confidence_badge import render_confidence_badge
from ui.components.citation_card import render_citation_card

render_privacy_banner()

with st.sidebar:
    st.markdown("### ⚡ Diagnostics")
    render_model_status()
    st.markdown("---")
    st.markdown("### 🎯 Agent Routing Intent")
    selected_intent = st.selectbox(
        "Target Domain Agent",
        ["general", "maintenance", "compliance", "lessons_learned"],
        format_func=lambda x: {
            "general": "💬 Copilot (General Operations)",
            "maintenance": "🔧 Maintenance Engineering",
            "compliance": "🛡️ Regulatory Compliance",
            "lessons_learned": "📚 Reliability & Lessons",
        }[x],
        help="Route query to a specialized domain agent or let the system auto-detect."
    )

st.markdown("<h1 style='color: #38BDF8;'>💬 Ask Plant Co-Pilot</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Ask complex operational, maintenance, or safety questions. The AI engine retrieves relevant SOPs and knowledge graph nodes to synthesize verified answers.</p>", unsafe_allow_html=True)
st.markdown("---")

API_URL = "http://127.0.0.1:8000"

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am your 100% offline Ops Brain Co-Pilot. Ask me anything about refinery pumps, maintenance work orders, safety compliance, or SOP procedures."}
    ]

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "citations" in msg and msg["citations"]:
            render_citation_card(msg["citations"])
        if "confidence" in msg:
            render_confidence_badge(msg["confidence"])
        if "actions" in msg and msg["actions"]:
            st.markdown("---")
            st.markdown("#### ⚡ Recommended Industrial Actions:")
            for act in msg["actions"]:
                st.markdown(f"- 🔸 **{act}**")
        if "alerts" in msg and msg["alerts"]:
            for alert in msg["alerts"]:
                st.error(f"🚨 {alert}")

# Chat Input Area
if prompt := st.chat_input("Ex: Why did P-204 mechanical seal fail? What are the OISD-116 requirements?"):
    # Append user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response Generation
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(" *Synthesizing verified industrial answer from RAG pipeline & graph...*")
        
        try:
            payload = {
                "query": prompt,
                "intent": selected_intent,
                "asset_tags": []
            }
            resp = requests.post(f"{API_URL}/api/v1/query", json=payload, timeout=180.0)
            
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "No answer generated.")
                citations = data.get("citations", [])
                confidence = data.get("confidence", "MEDIUM")
                actions = data.get("recommended_actions", [])
                alerts = data.get("alerts", [])
                
                # Render answer
                message_placeholder.markdown(answer)
                
                if alerts:
                    for alert in alerts:
                        st.error(f" {alert}")
                        
                render_confidence_badge(confidence)
                render_citation_card(citations)
                
                if actions:
                    st.markdown("---")
                    st.markdown("#### Recommended Industrial Actions:")
                    for act in actions:
                        st.markdown(f"- **{act}**")
                        
                # Store in history
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                    "confidence": confidence,
                    "actions": actions,
                    "alerts": alerts,
                })
            else:
                err_msg = f" API Error: {resp.status_code} - {resp.text}"
                message_placeholder.error(err_msg)
                st.session_state["messages"].append({"role": "assistant", "content": err_msg})
        except Exception as e:
            err_msg = f" Could not connect to local backend API: {e}. Please ensure `uvicorn api.app:app` is running on port 8000."
            message_placeholder.error(err_msg)
            st.session_state["messages"].append({"role": "assistant", "content": err_msg})
