"""
ui/components/citation_card.py
==============================
Renders the citation list returned from POST /api/v1/query:

    {"id": "[1]", "doc_id": "...", "title": "...", "score": 0.85, "snippet": "..."}
"""

import streamlit as st
from typing import Any, Dict, List


def render_citation_card(citations: List[Dict[str, Any]]) -> None:
    """Render citations as light, collapsible reference cards with a relevance bar."""
    if not citations:
        return

    st.markdown(
        "<p style='font-family:Space Grotesk; font-weight:700; font-size:0.85rem; "
        "text-transform:uppercase; letter-spacing:0.04em; color:#51607A; margin-top:18px;'>"
        "Referenced Documents</p>",
        unsafe_allow_html=True,
    )

    for i, cit in enumerate(citations):
        ref_id = cit.get("id") or f"[{i + 1}]"
        doc_id = cit.get("doc_id", "")
        title = cit.get("title") or doc_id or f"Document {i + 1}"
        score = cit.get("score", 0.0)
        score_pct = int(score * 100) if score <= 1.0 else int(score)
        snippet = cit.get("snippet") or cit.get("text") or "No preview available."

        bar_color = "#12875D" if score_pct >= 80 else ("#B7791F" if score_pct >= 60 else "#2563EB")

        with st.expander(f"{ref_id}  {title}  ·  relevance {score_pct}%", expanded=(i == 0)):
            st.markdown(
                f"""
                <div style="background:#FAFBFC; border:1px solid #E2E6ED; border-radius:8px; padding:14px 16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:#51607A;">{doc_id}</span>
                        <span style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:{bar_color}; font-weight:600;">{score_pct}% MATCH</span>
                    </div>
                    <div style="height:4px; background:#E2E6ED; border-radius:2px; margin-bottom:12px;">
                        <div style="height:100%; width:{score_pct}%; background:{bar_color}; border-radius:2px;"></div>
                    </div>
                    <div style="font-size:0.9rem; color:#28344A; line-height:1.55; font-style:italic;">
                        &ldquo;{snippet}&rdquo;
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
