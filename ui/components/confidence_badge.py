"""
ui/components/confidence_badge.py
==================================
Renders the HIGH / MEDIUM / LOW confidence pill returned alongside every
answer from POST /api/v1/query.
"""

import streamlit as st


def render_confidence_badge(confidence: str = "MEDIUM") -> None:
    """Render a confidence pill."""
    conf_upper = (confidence or "MEDIUM").upper()

    palette = {
        "HIGH": ("#0F5C3E", "#E4F5EC", "#BEE7D3", "●"),
        "LOW": ("#8C2A22", "#FBE7E4", "#F0BEB6", "●"),
    }
    text_c, bg_c, border_c, dot = palette.get(conf_upper, ("#8A5A0C", "#FDF3DF", "#F3DDA8", "●"))

    st.markdown(
        f"""
        <span style="
            display:inline-flex; align-items:center; gap:6px;
            font-family:'Space Grotesk',sans-serif; font-weight:700;
            font-size:0.72rem; letter-spacing:0.05em; text-transform:uppercase;
            color:{text_c}; background:{bg_c}; border:1px solid {border_c};
            padding:4px 12px; border-radius:20px;">
            <span style="color:{text_c};">{dot}</span> Confidence: {conf_upper}
        </span>
        """,
        unsafe_allow_html=True,
    )
