"""
ui/components/citation_card.py
==============================
Renders interactive citation cards displaying document titles, section headings,
relevance score progress bars, and expandable text snippets.
"""

import streamlit as st
from typing import Any, Dict, List


def render_citation_card(citations: List[Dict[str, Any]]):
    """Render a grid/list of interactive citations with relevance scores."""
    if not citations:
        return

    st.markdown("<h4 style='font-family: Outfit; color: #E2E8F0; margin-top: 20px;'>📚 Verified Document Citations</h4>", unsafe_allow_html=True)
    
    for idx, cit in enumerate(citations):
        title = cit.get("title") or cit.get("doc_id") or f"Document #{idx+1}"
        section = cit.get("section") or "General Section"
        score = cit.get("relevance_score", 0.0) if "relevance_score" in cit else cit.get("score", 0.85)
        score_pct = int(score * 100) if score <= 1.0 else int(score)
        snippet = cit.get("text") or cit.get("content") or "No text snippet available."
        
        # Color gradient based on score
        bar_color = "#10B981" if score_pct >= 80 else ("#F59E0B" if score_pct >= 60 else "#38BDF8")

        with st.expander(f"📖 [{idx+1}] {title} — {section} (Relevance: {score_pct}%)", expanded=(idx == 0)):
            st.markdown(
                f"""
                <style>
                .cit-container {{
                    background: rgba(15, 23, 42, 0.6);
                    border-left: 3px solid {bar_color};
                    padding: 12px 16px;
                    border-radius: 4px 8px 8px 4px;
                    font-family: 'Inter', sans-serif;
                }}
                .cit-meta {{
                    font-size: 0.8rem;
                    color: #94A3B8;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                }}
                .cit-snippet {{
                    font-size: 0.9rem;
                    color: #E2E8F0;
                    line-height: 1.5;
                    font-style: italic;
                }}
                </style>
                <div class="cit-container">
                    <div class="cit-meta">
                        <span><strong>Source:</strong> {title}</span>
                        <span><strong>Section:</strong> {section}</span>
                    </div>
                    <div class="cit-snippet">"{snippet}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
