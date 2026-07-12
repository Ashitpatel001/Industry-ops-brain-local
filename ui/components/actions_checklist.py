"""
ui/components/actions_checklist.py
===================================
Renders `recommended_actions` (a list of strings) from POST /api/v1/query
as an interactive field checklist rather than a flat bullet list.
"""

import streamlit as st
from typing import List


def render_actions_checklist(actions: List[str], key_prefix: str = "action") -> None:
    """Render recommended actions as tickable checklist items."""
    if not actions:
        return

    st.markdown(
        "<p style='font-family:Space Grotesk; font-weight:700; font-size:0.85rem; "
        "text-transform:uppercase; letter-spacing:0.04em; color:#51607A; margin:18px 0 8px 0;'>"
        "Recommended Field Actions</p>",
        unsafe_allow_html=True,
    )

    for i, act in enumerate(actions):
        checked = st.checkbox(act, key=f"{key_prefix}_{i}_{hash(act) % 10000}")
        style = "color:#8A9BB8; text-decoration:line-through;" if checked else "color:#0B1F3A;"
        # visual echo under the native checkbox for a field-ticket feel
        st.markdown(
            f"<div style='margin:-10px 0 6px 30px; font-family:IBM Plex Mono; font-size:0.72rem; {style}'>"
            f"{'DONE' if checked else 'OPEN'}</div>",
            unsafe_allow_html=True,
        )
